package pe.agendaclara.app;
import android.content.Context;
import android.net.Uri;
import java.io.*;
import java.util.Arrays;

/** Task-only AES backup. Excludes linked WhatsApp sessions and message history. */
public final class SecureTaskBackup {
    private static final int MAX_FILE=8*1024*1024+256;
    private SecureTaskBackup(){}
    public static int exportTo(Context context,Uri uri,char[] password)throws Exception{
        byte[] data=null,sealed=null;
        try{
            data=TaskBackup.exportBytes(context);sealed=SecureArchive.encrypt(data,password);
            try(OutputStream out=context.getContentResolver().openOutputStream(uri,"wt")){
                if(out==null)throw new IOException("No se pudo crear el archivo cifrado.");
                out.write(sealed);
            }
            return Store.get(context).all().size();
        }finally{
            if(data!=null)Arrays.fill(data,(byte)0);
            if(sealed!=null)Arrays.fill(sealed,(byte)0);
            if(password!=null)Arrays.fill(password,'\0');
        }
    }
    public static int importFrom(Context context,Uri uri,char[] password)throws Exception{
        byte[] sealed=null,plain=null;
        try{
            try(InputStream in=context.getContentResolver().openInputStream(uri)){
                if(in==null)throw new IOException("No se pudo abrir la copia cifrada.");
                ByteArrayOutputStream out=new ByteArrayOutputStream();
                byte[] part=new byte[8192];int n;
                while((n=in.read(part))!=-1){
                    if(out.size()+n>MAX_FILE)throw new IOException("Archivo demasiado grande.");
                    out.write(part,0,n);
                }
                sealed=out.toByteArray();
            }
            plain=SecureArchive.decrypt(sealed,password);
            return TaskBackup.importBytes(context,plain);
        }finally{
            if(plain!=null)Arrays.fill(plain,(byte)0);
            if(sealed!=null)Arrays.fill(sealed,(byte)0);
            if(password!=null)Arrays.fill(password,'\0');
        }
    }
}