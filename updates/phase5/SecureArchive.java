package pe.agendaclara.app;

import java.io.IOException;
import java.security.SecureRandom;
import java.security.GeneralSecurityException;
import java.util.Arrays;
import javax.crypto.Cipher;
import javax.crypto.AEADBadTagException;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.SecretKeySpec;

/** Password-based, authenticated offline archive. No credentials are stored. */
public final class SecureArchive {
    private static final byte[] MAGIC=new byte[]{65,67,66,75,1};
    private static final int SALT=16,IV=12,TAG=128,ROUNDS=180000,LIMIT=8*1024*1024;
    private SecureArchive(){}
    private static SecretKeySpec derive(char[] password,byte[] salt)throws GeneralSecurityException{
        PBEKeySpec p=new PBEKeySpec(password,salt,ROUNDS,256);byte[] key=null;
        try{
            key=SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(p).getEncoded();
            return new SecretKeySpec(key,"AES");
        }finally{p.clearPassword();if(key!=null)Arrays.fill(key,(byte)0);}
    }
    private static void validatePassword(char[] password)throws IOException{
        if(password==null||password.length<10||password.length>256)
            throw new IOException("Usa una contraseña de entre 10 y 256 caracteres.");
    }
    public static byte[] encrypt(byte[] data,char[] password)throws Exception{
        validatePassword(password);
        if(data==null||data.length>LIMIT)throw new IOException("Copia superior al tamaño permitido.");
        byte[] salt=new byte[SALT],iv=new byte[IV];SecureRandom rand=new SecureRandom();
        rand.nextBytes(salt);rand.nextBytes(iv);
        byte[] header=new byte[MAGIC.length+SALT+IV];
        System.arraycopy(MAGIC,0,header,0,MAGIC.length);
        System.arraycopy(salt,0,header,MAGIC.length,SALT);
        System.arraycopy(iv,0,header,MAGIC.length+SALT,IV);
        Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE,derive(password,salt),new GCMParameterSpec(TAG,iv));
        cipher.updateAAD(header);
        byte[] sealed=cipher.doFinal(data),output=Arrays.copyOf(header,header.length+sealed.length);
        System.arraycopy(sealed,0,output,header.length,sealed.length);Arrays.fill(sealed,(byte)0);
        return output;
    }
    public static byte[] decrypt(byte[] bytes,char[] password)throws Exception{
        validatePassword(password);
        if(bytes==null||bytes.length<MAGIC.length+SALT+IV+16||bytes.length>LIMIT+256)
            throw new IOException("Archivo cifrado inválido o demasiado grande.");
        for(int i=0;i<MAGIC.length;i++)if(bytes[i]!=MAGIC[i])
            throw new IOException("Formato incompatible: se requiere un .acbak de Agenda Clara.");
        int headerLen=MAGIC.length+SALT+IV;
        byte[] salt=Arrays.copyOfRange(bytes,MAGIC.length,MAGIC.length+SALT);
        byte[] iv=Arrays.copyOfRange(bytes,MAGIC.length+SALT,headerLen);
        Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.DECRYPT_MODE,derive(password,salt),new GCMParameterSpec(TAG,iv));
        cipher.updateAAD(bytes,0,headerLen);
        try{return cipher.doFinal(bytes,headerLen,bytes.length-headerLen);}
        catch(AEADBadTagException e){throw new IOException("Contraseña incorrecta o archivo modificado.");}
    }
}