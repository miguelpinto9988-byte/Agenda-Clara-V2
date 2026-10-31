package pe.agendaclara.app;

import android.content.Context;
import android.graphics.drawable.Drawable;
import android.widget.Button;
import android.widget.ImageView;
import android.content.res.Resources;

/** Untinted transparent PNG artwork extracted from the approved reference sheet.
 * Compound drawables remain attached in both pressed and unpressed button states.
 */
public final class ApprovedPng {
    private ApprovedPng(){}
    private static String key(String name){
        if(name==null)return "folder";
        switch(name){
            case "category":case "folder":return "folder";
            case "calendar":case "date":return "date";
            case "device-calendar":return "device_calendar";
            case "google-calendar":return "google_calendar";
            case "clock":case "time":return "time";
            case "notification":case "notifications":return "notification";
            case "bell":return "bell";
            case "repetition":case "repeat":return "repeat";
            case "notes":case "edit":return "notes";
            case "check":case "save":return "save";
            case "whatsapp":return "whatsapp";
            case "backup":case "cloud":return "backup";
            case "widgets":return "widgets";
            case "settings":case "gear":return "settings";
            case "back":return "back";
            case "help":return "help";
            case "photo":return "photo";
            case "manual":return "manual";
            case "schedule":return "schedule";
            case "study":return "study";
            case "book":return "book";
            case "reminder-settings":return "reminder_settings";
            case "health":case "projects":case "work":case "personal":case "travel":
            case "finance":case "sport":case "leisure":case "food":case "family":case "other":return "cat_"+name;
            case "palette":case "color":return "palette";
            default:return name.replace('-','_');
        }
    }
    public static Drawable drawable(Context c,String name){
        String resource="ic_ref_"+key(name);
        int id=c.getResources().getIdentifier(resource,"drawable",c.getPackageName());
        if(id!=0){
            Drawable d=c.getDrawable(id);
            if(d!=null)return d.mutate();
        }
        // Old and imported custom icon names remain visible.
        return new ModernGlyph(name,ModernGlyph.BLUE);
    }
    public static ImageView view(Context c,String name,int pixelsDp){
        ImageView iv=new ImageView(c);
        iv.setImageDrawable(drawable(c,name));
        iv.setScaleType(ImageView.ScaleType.FIT_CENTER);
        iv.setContentDescription(name);
        int padding=UiDesign.dp(c,1),size=UiDesign.dp(c,pixelsDp);
        iv.setMinimumWidth(size);iv.setMinimumHeight(size);
        iv.setPadding(padding,padding,padding,padding);
        return iv;
    }
    public static void button(Button b,String name,int iconDp){
        Drawable d=drawable(b.getContext(),name);
        int size=UiDesign.dp(b.getContext(),iconDp);
        d.setBounds(0,0,size,size);
        b.setCompoundDrawablesRelative(d,null,null,null);
        b.setCompoundDrawablePadding(UiDesign.dp(b.getContext(),8));
        if(b.getContentDescription()==null)b.setContentDescription(b.getText());
    }
}
