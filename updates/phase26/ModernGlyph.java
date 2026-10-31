package pe.agendaclara.app;

import android.content.Context;
import android.content.res.ColorStateList;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.ColorFilter;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.PixelFormat;
import android.graphics.Rect;
import android.graphics.drawable.Drawable;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.RippleDrawable;
import android.widget.Button;
import android.widget.ImageView;

/** Stable, multi-colour native iconography based on the approved design reference.
 * Canvas drawables are not removed by press states or parent rerenders.
 */
public final class ModernGlyph extends Drawable {
    public static final int BLUE=0xff3768f7, CYAN=0xff13b6e6,
        AMBER=0xffffab20, VIOLET=0xff844fee, GREEN=0xff16b778,
        CORAL=0xfff45b73, DARK=0xff17305c;
    private final Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
    private final String type;
    private final int accent;
    private final boolean fill;
    public ModernGlyph(String type,int accent){this(type,accent,false);}
    public ModernGlyph(String type,int accent,boolean fill){this.type=type;this.accent=accent;this.fill=fill;}
    private void pen(int color,float width){
        p.setStyle(Paint.Style.STROKE);p.setColor(color);p.setStrokeWidth(width);
        p.setStrokeCap(Paint.Cap.ROUND);p.setStrokeJoin(Paint.Join.ROUND);
    }
    private void solid(int color){p.setStyle(Paint.Style.FILL);p.setColor(color);}
    private void line(Canvas c,float x,float y,float x2,float y2){c.drawLine(x,y,x2,y2,p);}
    private void round(Canvas c,float x,float y,float x2,float y2,float r){c.drawRoundRect(x,y,x2,y2,r,r,p);}
    private void blob(Canvas c,int color,float x,float y,float radius){solid(color);c.drawCircle(x,y,radius,p);}
    @Override public void draw(Canvas original){
        Rect b=getBounds();original.save();
        original.translate(b.left,b.top);original.scale(b.width()/24f,b.height()/24f);
        Canvas c=original;int a=accent==0?BLUE:accent;
        // Each glyph intentionally has two or three colours. No font/emoji dependency.
        switch(type){
            case "folder":
            case "category":
                solid(UiDesign.blend(0xffffffff,a,.22f));round(c,2,7,22,20,3);
                pen(a,2.4f);Path path=new Path();path.moveTo(2,9);path.lineTo(2,6);
                path.quadTo(2,4,4,4);path.lineTo(10,4);path.lineTo(12,7);
                path.lineTo(20,7);path.quadTo(22,7,22,9);path.lineTo(22,19);
                path.quadTo(22,21,20,21);path.lineTo(4,21);
                path.quadTo(2,21,2,19);path.close();c.drawPath(path,p);
                pen(CYAN,2.3f);line(c,5,11,18,11);break;
            case "date":
            case "calendar":
            case "device-calendar":
                solid(0xffdbe8ff);round(c,3,4,21,21,3);
                pen(a,2.25f);round(c,3,4,21,21,3);line(c,3,10,21,10);
                line(c,8,2,8,6);line(c,16,2,16,6);
                blob(c,AMBER,8,14,1.5f);blob(c,CYAN,15,14,1.5f);blob(c,VIOLET,11.5f,18,1.5f);break;
            case "google-calendar":
                solid(0xffeaf2ff);round(c,3,4,21,21,3);
                solid(0xff4285f4);c.drawRect(3,4,12,8,p);solid(0xff34a853);c.drawRect(12,4,21,8,p);
                solid(0xfffbbc05);c.drawRect(3,8,6,21,p);solid(0xffea4335);c.drawRect(18,8,21,21,p);
                pen(DARK,1.4f);round(c,3,4,21,21,3);pen(a,2.3f);line(c,8,13,16,13);line(c,9,17,15,17);break;
            case "time":
            case "clock":
                pen(a,2.4f);c.drawCircle(12,12,9,p);
                pen(CYAN,2.8f);line(c,12,6.5f,12,12);line(c,12,12,16.5f,15);blob(c,AMBER,12,12,1.4f);break;
            case "bell":
            case "notification":
                solid(0xffffedca);round(c,8,5,16,16,4);
                pen(AMBER,2.3f);Path bell=new Path();bell.moveTo(5,17);bell.lineTo(7,14);
                bell.lineTo(7,10);bell.cubicTo(7,3,17,3,17,10);bell.lineTo(17,14);
                bell.lineTo(19,17);bell.close();c.drawPath(bell,p);
                pen(CORAL,2.4f);line(c,10,20,14,20);break;
            case "repeat":
                pen(GREEN,2.7f);c.drawArc(4,4,20,20,206,220,false,p);
                pen(CYAN,2.4f);c.drawArc(4,4,20,20,25,135,false,p);
                pen(GREEN,2.5f);line(c,3,8,4,13);line(c,4,13,9,12);
                pen(CYAN,2.5f);line(c,21,16,20,11);line(c,20,11,15,12);break;
            case "notes":
                solid(0xffe8f0ff);round(c,5,3,19,22,2);
                pen(a,2.25f);round(c,5,3,19,22,2);
                pen(CYAN,2.5f);line(c,8,9,16,9);line(c,8,13,16,13);
                pen(VIOLET,2.5f);line(c,8,17,13,17);break;
            case "save":
            case "check":
                solid(0xffd9faec);round(c,3,3,21,21,3);
                pen(GREEN,2.4f);round(c,3,3,21,21,3);
                pen(0xffffffff,3f);line(c,7,12,10.5f,15);line(c,10.5f,15,17,8);break;
            case "whatsapp":
                blob(c,0xff22c85d,12,12,10);
                pen(0xffffffff,1.7f);Path w=new Path();w.moveTo(6,17);w.lineTo(7,14);
                w.cubicTo(5,8,9,5,13,5);w.cubicTo(19,5,21,13,17,17);
                w.cubicTo(14,20,10,19,8,18);w.close();c.drawPath(w,p);
                pen(0xffffffff,2.3f);c.drawArc(9,8,17,16,50,125,false,p);break;
            case "backup":
                solid(0xffe7f0ff);round(c,3,10,21,20,5);
                pen(a,2.3f);c.drawArc(2,6,22,22,185,170,false,p);
                pen(CYAN,2.8f);line(c,12,9,12,17);line(c,9,14,12,17);line(c,12,17,15,14);break;
            case "widgets":
                solid(0xffe9e4ff);round(c,3,3,10,10,2);round(c,14,3,21,10,2);
                round(c,3,14,10,21,2);round(c,14,14,21,21,2);
                pen(VIOLET,2.1f);round(c,3,3,10,10,2);round(c,14,3,21,10,2);
                pen(BLUE,2.1f);round(c,3,14,10,21,2);round(c,14,14,21,21,2);break;
            case "settings":
                pen(a,2.5f);c.drawCircle(12,12,7,p);c.drawCircle(12,12,2.8f,p);
                pen(VIOLET,2.5f);for(int i=0;i<8;i++){double t=i*Math.PI/4;
                    line(c,(float)(12+8*Math.cos(t)),(float)(12+8*Math.sin(t)),
                        (float)(12+10*Math.cos(t)),(float)(12+10*Math.sin(t)));}break;
            case "photo":
                solid(0xffe8f3ff);round(c,2,6,22,20,3);
                pen(a,2.3f);round(c,2,6,22,20,3);
                pen(CYAN,2.5f);c.drawCircle(12,13,4,p);
                blob(c,AMBER,18,7,1.8f);break;
            case "manual":
            case "edit":
                pen(a,2.8f);line(c,5,19,9,18);line(c,9,18,19,8);
                pen(AMBER,3f);line(c,19,8,16,5);
                pen(VIOLET,2.5f);line(c,5,19,4,21);break;
            case "back":
                pen(a,2.7f);line(c,14,4,6,12);line(c,6,12,14,20);
                pen(CYAN,2.4f);line(c,7,12,21,12);break;
            case "help":
                pen(a,2.5f);c.drawCircle(12,12,9,p);
                pen(VIOLET,2.4f);c.drawArc(8,6,16,15,190,240,false,p);
                blob(c,CYAN,12,18,1.3f);break;
            default:
                pen(a,2.6f);c.drawCircle(12,12,9,p);
                blob(c,CYAN,12,12,3);
        }
        original.restore();
    }
    @Override public void setAlpha(int alpha){p.setAlpha(alpha);invalidateSelf();}
    @Override public void setColorFilter(ColorFilter filter){p.setColorFilter(filter);invalidateSelf();}
    @Override public int getOpacity(){return PixelFormat.TRANSLUCENT;}
    @Override public int getIntrinsicWidth(){return 24;}
    @Override public int getIntrinsicHeight(){return 24;}
    public static ImageView view(Context context,String name,int color,int sizeDp){
        ImageView iv=new ImageView(context);
        iv.setImageDrawable(new ModernGlyph(name,color));
        iv.setContentDescription(name);
        int px=UiDesign.dp(context,sizeDp);
        iv.setMinimumWidth(px);iv.setMinimumHeight(px);
        iv.setPadding(UiDesign.dp(context,2),UiDesign.dp(context,2),UiDesign.dp(context,2),UiDesign.dp(context,2));
        return iv;
    }
    public static void button(Button button,String name,int color,int iconDp){
        ModernGlyph glyph=new ModernGlyph(name,color);
        int size=UiDesign.dp(button.getContext(),iconDp);
        glyph.setBounds(0,0,size,size);
        button.setCompoundDrawables(glyph,null,null,null);
        button.setCompoundDrawablePadding(UiDesign.dp(button.getContext(),8));
        // Important: icon is a stable compound drawable, not a transient overlay.
        if(button.getContentDescription()==null)button.setContentDescription(button.getText());
    }
    public static GradientDrawable rounded(Context context,int color,int border,int radius){
        GradientDrawable shape=UiDesign.shape(context,color,radius,0);
        if(border!=0)shape.setStroke(UiDesign.dp(context,1),border);
        return shape;
    }
}
