package pe.agendaclara.app;

/** Keyboard height transitions without Android runtime or private user data. */
public final class DialogResizePolicyTest {
    static void require(boolean ok,String what){if(!ok)throw new AssertionError(what);}
    public static void main(String[] args){
        int wrap=DialogResizePolicy.WRAP_CONTENT;
        require(DialogResizePolicy.height(wrap,-1,850,250,false)==wrap,"initial natural height");
        require(DialogResizePolicy.height(wrap,850,450,600,false)==450,"keyboard clamps oversized dialog");
        require(DialogResizePolicy.height(450,450,450,450,false)==450,"stable keyboard must not oscillate");
        require(DialogResizePolicy.height(450,450,850,450,true)==wrap,"hiding keyboard restores wrap");
        require(DialogResizePolicy.height(450,450,850,450,false)==wrap,"growing viewport restores wrap");
        require(DialogResizePolicy.height(450,450,450,450,true)==wrap,"IME transition restores despite stale viewport");
        require(DialogResizePolicy.height(wrap,850,850,520,false)==wrap,"short dialogs stay natural");
        require(DialogResizePolicy.height(450,450,420,450,false)==420,"smaller viewport reclamps");
        require(DialogResizePolicy.height(wrap,850,400,500,false)==400,"small viewport clamps");
        require(DialogResizePolicy.height(420,420,850,420,false)==wrap,"orientation/viewport expansion restores");
        System.out.println("PASS: 10 dialog keyboard/viewport height transitions");
    }
}
