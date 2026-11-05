package pe.agendaclara.app;

import com.tom_roush.pdfbox.text.PDFTextStripper;
import com.tom_roush.pdfbox.text.TextPosition;
import java.io.IOException;
import java.util.List;

/**
 * Preserves strongly separated PDF columns as tab stops. Short gaps remain
 * normal text; adjacent words are not promoted into separate table cells.
 */
public final class SyllabusColumnTextStripper extends PDFTextStripper {
    public SyllabusColumnTextStripper() throws IOException {
        super();
        setSortByPosition(true);
    }
    @Override protected void writeString(String value,List<TextPosition> positions)
            throws IOException {
        if(positions==null||positions.size()<2){
            super.writeString(value,positions);return;
        }
        StringBuilder out=new StringBuilder();
        TextPosition prior=null;boolean sawColumn=false;
        for(TextPosition position:positions){
            if(prior!=null){
                float gap=position.getXDirAdj()-
                        (prior.getXDirAdj()+prior.getWidthDirAdj());
                float minGap=Math.max(20f,position.getWidthOfSpace()*4f);
                if(gap>minGap){
                    out.append('\t');sawColumn=true;
                }else if(gap>Math.max(2f,position.getWidthOfSpace()*.7f)){
                    out.append(' ');
                }
            }
            out.append(position.getUnicode());
            prior=position;
        }
        super.writeString(sawColumn?out.toString():value,positions);
    }
}
