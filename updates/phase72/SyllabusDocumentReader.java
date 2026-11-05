package pe.agendaclara.app;

import android.content.Context;
import android.net.Uri;
import android.graphics.Bitmap;
import com.tom_roush.pdfbox.rendering.PDFRenderer;
import com.google.android.gms.tasks.Tasks;
import com.google.mlkit.vision.common.InputImage;
import com.google.mlkit.vision.text.TextRecognition;
import com.google.mlkit.vision.text.latin.TextRecognizerOptions;
import android.util.Xml;
import com.tom_roush.pdfbox.android.PDFBoxResourceLoader;
import com.tom_roush.pdfbox.pdmodel.PDDocument;
import com.tom_roush.pdfbox.text.PDFTextStripper;
import org.apache.poi.hwpf.HWPFDocument;
import org.apache.poi.hwpf.extractor.WordExtractor;
import org.xmlpull.v1.XmlPullParser;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/** Offline PDF/Word text extraction, input size bounded, no uploading. */
public final class SyllabusDocumentReader {
    private static final int MAX_INPUT=12*1024*1024,MAX_TEXT=300000,MAX_PAGES=120;
    private SyllabusDocumentReader(){}
    public static List<SyllabusEventParser.Page> read(Context context,Uri uri,String filename)
            throws Exception{
        byte[] bytes;
        try(InputStream in=context.getContentResolver().openInputStream(uri)){
            if(in==null)throw new IOException("No se pudo abrir el documento");
            ByteArrayOutputStream out=new ByteArrayOutputStream();
            byte[] buffer=new byte[8192];int n;
            while((n=in.read(buffer))!=-1){
                if(out.size()+n>MAX_INPUT)throw new IOException("Documento demasiado grande (máximo 12 MB)");
                out.write(buffer,0,n);
            }
            bytes=out.toByteArray();
        }
        if(bytes.length<8)throw new IOException("Documento vacío o incompleto");
        String name=filename==null?"":filename.toLowerCase(java.util.Locale.ROOT);
        if(name.endsWith(".pdf"))return pdf(context,bytes);
        if(name.endsWith(".docx"))return docx(bytes);
        if(name.endsWith(".doc"))return doc(bytes);
        throw new IOException("Tipo de documento no admitido: PDF, DOC o DOCX");
    }
    private static List<SyllabusEventParser.Page> pdf(Context context,byte[] bytes)
            throws Exception{
        PDFBoxResourceLoader.init(context.getApplicationContext());
        ArrayList<SyllabusEventParser.Page> pages=new ArrayList<>();
        if(bytes[0]!='%'||bytes[1]!='P'||bytes[2]!='D'||bytes[3]!='F')
            throw new IOException("El archivo no contiene un PDF válido");
        try(PDDocument document=PDDocument.load(bytes)){
            int count=document.getNumberOfPages();
            if(count>MAX_PAGES)throw new IOException("Máximo 120 páginas");
            PDFTextStripper stripper=new PDFTextStripper();
            int total=0,scanned=0;
            PDFRenderer renderer=new PDFRenderer(document);
            com.google.mlkit.vision.text.TextRecognizer ocr=null;
            try {
            for(int i=1;i<=count;i++){
                stripper.setStartPage(i);stripper.setEndPage(i);
                String text=stripper.getText(document);
                if(text.trim().length()<12){
                    if(++scanned>20)throw new IOException("PDF escaneado: máximo 20 páginas OCR por documento");
                    if(ocr==null)ocr=TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS);
                    Bitmap bitmap=renderer.renderImageWithDPI(i-1,140);
                    try{text=Tasks.await(ocr.process(InputImage.fromBitmap(bitmap,0))).getText();}
                    finally{bitmap.recycle();}
                }
                total+=text.length();
                if(total>MAX_TEXT)throw new IOException("El texto del documento supera el límite");
                pages.add(new SyllabusEventParser.Page(i,text));
            }
            } finally {if(ocr!=null)ocr.close();}
        }
        return pages;
    }
    private static List<SyllabusEventParser.Page> doc(byte[] bytes)throws Exception{
        ArrayList<SyllabusEventParser.Page> pages=new ArrayList<>();
        try(HWPFDocument document=new HWPFDocument(new ByteArrayInputStream(bytes));
            WordExtractor extractor=new WordExtractor(document)){
            String text=extractor.getText();
            if(text.length()>MAX_TEXT)throw new IOException("Texto excesivo");
            // Word .doc doesn't expose reliable physical pages without layout.
            pages.add(new SyllabusEventParser.Page(0,text));
        }
        return pages;
    }
    private static List<SyllabusEventParser.Page> docx(byte[] bytes)throws Exception{
        StringBuilder text=new StringBuilder();
        boolean found=false;
        try(ZipInputStream zip=new ZipInputStream(new ByteArrayInputStream(bytes))){
            ZipEntry entry;int entries=0;
            while((entry=zip.getNextEntry())!=null){
                if(++entries>500)throw new IOException("DOCX con demasiadas entradas");
                if(!"word/document.xml".equals(entry.getName()))continue;
                found=true;
                ByteArrayOutputStream out=new ByteArrayOutputStream();
                byte[] buffer=new byte[8192];int count;
                while((count=zip.read(buffer))!=-1){
                    if(out.size()+count>MAX_TEXT*4)throw new IOException("DOCX demasiado grande");
                    out.write(buffer,0,count);
                }
                XmlPullParser parser=Xml.newPullParser();
                parser.setInput(new ByteArrayInputStream(out.toByteArray()),"UTF-8");
                int event;
                while((event=parser.next())!=XmlPullParser.END_DOCUMENT){
                    if(event==XmlPullParser.START_TAG&&"t".equals(parser.getName())){
                        text.append(parser.nextText());
                        if(text.length()>MAX_TEXT)throw new IOException("Texto excesivo");
                    }
                    if(event==XmlPullParser.END_TAG && ("p".equals(parser.getName())
                            || "tr".equals(parser.getName())))text.append('\n');
                }
                break;
            }
        }
        if(!found)throw new IOException("No se encontró el documento de Word");
        ArrayList<SyllabusEventParser.Page> pages=new ArrayList<>();
        pages.add(new SyllabusEventParser.Page(0,text.toString()));
        return pages;
    }
}
