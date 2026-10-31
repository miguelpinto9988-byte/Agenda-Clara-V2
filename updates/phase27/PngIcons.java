package pe.agendaclara.app;
import android.content.Context;
import android.graphics.drawable.Drawable;
import android.graphics.drawable.RippleDrawable;
import android.graphics.drawable.BitmapDrawable;
import android.graphics.drawable.Drawable.ConstantState;
import android.widget.Button;
import android.widget.ImageView;

/** Render actual 96x96 transparent PNG resources, never text glyphs or emoji.
 * PNG artwork is independent of the button's ripple/pressed background.
 */
public final class PngIcons {
    private PngIcons(){}
    public static final String[] CATEGORY_SYMBOLS={
        "folder","school","work","heart","home","travel","book","projects",
        "calendar","bell","urgent","color","photo","check","notes","widgets"
    };
    public static final String[] CATEGORY_LABELS={
        "General","Estudios","Trabajo","Salud","Personal","Viajes","Lectura","Proyectos",
        "Calendario","Recordatorios","Importantes","Creatividad","Fotografía","Objetivos","Notas","Otros"
    };
    public static String safe(String requested){
        if(requested==null||requested.length()>24)return "folder";
        for(String s:CATEGORY_SYMBOLS)if(s.equals(requested))return requested;
        for(String s:new String[]{"date","time","clock","bell","repeat","notes","check",
            "whatsapp","google_calendar","device_calendar","backup","cloud","settings",
            "photo","manual","help","back","save","trash","lock","key","search",
            "color","urgent","notification","camera","pencil","edit","gear","book"})
            if(s.equals(requested))return s;
        return "folder";
    }
    public static int id(Context context,String name){
        String path="agenda_icon_"+safe(name);
        int found=context.getResources().getIdentifier(path,"drawable",context.getPackageName());
        if(found==0)found=R.drawable.agenda_icon_folder;
        return found;
    }
    public static ImageView view(Context c,String name,int sizeDp){
        ImageView iv=new ImageView(c);iv.setImageResource(id(c,name));
        iv.setScaleType(ImageView.ScaleType.FIT_CENTER);
        int px=UiDesign.dp(c,sizeDp);iv.setMinimumWidth(px);iv.setMinimumHeight(px);
        iv.setContentDescription(CATEGORY_LABELS[0].equals(name)?"General":name);
        iv.setPadding(UiDesign.dp(c,1),UiDesign.dp(c,1),UiDesign.dp(c,1),UiDesign.dp(c,1));
        return iv;
    }
    /** Compatibility signature for existing colour-aware native calls. */
    public static ImageView view(Context c,String name,int accent,int sizeDp){
        return view(c,name,sizeDp);
    }
    public static void button(Button b,String name,int accent,int sizeDp){
        button(b,name,sizeDp);
    }
    public static void button(Button b,String name,int sizeDp){
        if("new_task_button".equals(b.getTag()))return;
        Drawable glyph=b.getContext().getDrawable(id(b.getContext(),name));
        if(glyph==null)return;
        int size=UiDesign.dp(b.getContext(),sizeDp);
        glyph.setBounds(0,0,size,size);
        b.setCompoundDrawables(glyph,null,null,null);
        b.setCompoundDrawablePadding(UiDesign.dp(b.getContext(),7));
        // Never put the PNG inside RippleDrawable; pressed state may replace backgrounds.
    }
}
