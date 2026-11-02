package pe.agendaclara.app;

/** Pure height transition logic shared by notes, tasks, quick tasks and pickers. */
final class DialogResizePolicy {
    static final int WRAP_CONTENT=-2;
    private DialogResizePolicy(){}
    static int height(int current,int priorMaximum,int maximum,int measured,boolean keyboardClosed){
        if(maximum<=0)throw new IllegalArgumentException("maximum");
        // After the IME closes, release any fixed height left over from the keyboard.
        if(priorMaximum<0||maximum>priorMaximum||keyboardClosed)return WRAP_CONTENT;
        if(measured>maximum)return maximum;
        if(current>0&&maximum<priorMaximum)return Math.min(current,maximum);
        return current;
    }
}
