import pe.agendaclara.app.SecureArchive;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
public final class Phase5Tests {
  static int checks=0;
  static void check(boolean ok,String name){checks++;if(!ok)throw new AssertionError(name);}
  public static void main(String[] args)throws Exception {
    byte[] data="Agenda Clara tareas: 2026".getBytes(StandardCharsets.UTF_8);
    char[] pass="contraseña-de-ensayo-larga".toCharArray();
    byte[] encrypted=SecureArchive.encrypt(data,pass);
    check(encrypted.length>data.length+30,"header and tag");
    check(!Arrays.equals(encrypted,data),"encrypted");
    check(Arrays.equals(SecureArchive.decrypt(encrypted,pass),data),"round trip");
    check(!Arrays.equals(encrypted,SecureArchive.encrypt(data,pass)),"random IV+salt");
    boolean rejected=false;
    try{SecureArchive.decrypt(encrypted,"contraseña-equivocada".toCharArray());}catch(java.io.IOException e){rejected=true;}
    check(rejected,"wrong password");
    byte[] tampered=encrypted.clone();tampered[tampered.length-1]^=1;
    rejected=false;try{SecureArchive.decrypt(tampered,pass);}catch(java.io.IOException e){rejected=true;}check(rejected,"tampered payload");
    tampered=encrypted.clone();tampered[0]^=1;
    rejected=false;try{SecureArchive.decrypt(tampered,pass);}catch(java.io.IOException e){rejected=true;}check(rejected,"tampered version");
    rejected=false;try{SecureArchive.encrypt(data,"too-short".toCharArray());}catch(java.io.IOException e){rejected=true;}check(rejected,"minimum password");
    check(SecureArchive.decrypt(SecureArchive.encrypt(new byte[0],pass),pass).length==0,"empty plaintext");
    System.out.println("PASS: "+checks+" AES-GCM backup tests");
  }
}