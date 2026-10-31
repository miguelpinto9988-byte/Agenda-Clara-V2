package pe.agendaclara.app;

import android.animation.AnimatorSet;
import android.animation.ObjectAnimator;
import android.animation.StateListAnimator;
import android.animation.ValueAnimator;
import android.app.Activity;
import android.content.res.ColorStateList;
import android.graphics.Canvas;
import android.graphics.ColorFilter;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.PixelFormat;
import android.graphics.Rect;
import android.graphics.Typeface;
import android.graphics.drawable.Drawable;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.RippleDrawable;
import android.os.Build;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

/** Unified native design tokens, scalable outline icons and reduced-motion controls.
 * Deliberately not applied to the approved top-right plus artwork/motion.
 */
public final class UiDesign {
    private UiDesign(){}
    public static final int BG=0xfff5f8ff,INK=0xff14244d,BLUE=0xff3b5ff1,BLUE2=0xff6b5dec;
    public static final int MUTED=0xff60738f,PALE=0xffeef2ff,BORDER=0xffdce5f5;
    public static final int SUCCESS=0xff15977a,WARNING=0xffcf7b16,ERROR=0xffe24e63;
    public static final int SURFACE=0xffffffff;
    public static int dp(android.content.Context c,float size){return Math.round(size*c.getResources().getDisplayMetrics().density);}
    public static GradientDrawable shape(android.content.Context c,int color,int radius,int stroke) {
        GradientDrawable g=new GradientDrawable();g.setColor(color);g.setCornerRadius(dp(c,radius));
        if(stroke!=0)g.setStroke(dp(c,1),stroke);
        return g;
    }
    public static GradientDrawable gradient(android.content.Context c,int radius) {
        GradientDrawable g=new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT,new int[]{BLUE,BLUE2});
        g.setCornerRadius(dp(c,radius));return g;
    }
    public static void text(TextView t,boolean heavy) {
        t.setTypeface(Typeface.create(heavy?"sans-serif-medium":"sans-serif",Typeface.NORMAL));
        t.setIncludeFontPadding(true);
        if(Build.VERSION.SDK_INT>=21)t.setLetterSpacing(heavy?-0.012f:0f);
    }
    public static void button(Button b,boolean primary) {
        b.setAllCaps(false);b.setMinimumHeight(dp(b.getContext(),48));
        b.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));
        b.setTextColor(primary?0xffffffff:BLUE);b.setPadding(dp(b.getContext(),14),dp(b.getContext(),8),dp(b.getContext(),14),dp(b.getContext(),8));
        b.setBackground(new RippleDrawable(ColorStateList.valueOf(primary?0x32ffffff:0x183b5ff1),
             primary?gradient(b.getContext(),16):shape(b.getContext(),PALE,16,BORDER),null));
        b.setElevation(primary?dp(b.getContext(),2):0f);
        if(Build.VERSION.SDK_INT>=26&&ValueAnimator.areAnimatorsEnabled()) {
            StateListAnimator states=new StateListAnimator();
            AnimatorSet down=new AnimatorSet();down.playTogether(
               ObjectAnimator.ofFloat(b,"scaleX",1f,0.975f),ObjectAnimator.ofFloat(b,"scaleY",1f,0.975f));down.setDuration(90);
            AnimatorSet up=new AnimatorSet();up.playTogether(
               ObjectAnimator.ofFloat(b,"scaleX",0.975f,1f),ObjectAnimator.ofFloat(b,"scaleY",0.975f,1f));up.setDuration(130);
            states.addState(new int[]{android.R.attr.state_pressed},down);
            states.addState(new int[]{},up);b.setStateListAnimator(states);
        }
    }
    public static void input(TextView v){
        v.setBackground(shape(v.getContext(),SURFACE,17,BORDER));
        v.setPadding(dp(v.getContext(),14),dp(v.getContext(),12),dp(v.getContext(),14),dp(v.getContext(),12));
        v.setMinimumHeight(dp(v.getContext(),50));
        v.setTextColor(INK);text(v,false);
    }
    public static void card(View v){
        v.setBackground(shape(v.getContext(),SURFACE,20,BORDER));
        v.setElevation(dp(v.getContext(),2));
    }
    public static void actionIcon(Button b,String caption) {
        if(caption==null||caption.equals("＋"))return; // approved header plus is untouched
        String s=caption.toLowerCase(java.util.Locale.ROOT);String name=null;
        if(s.contains("guardar"))name="save";
        else if(s.contains("borrar")||s.contains("eliminar"))name="trash";
        else if(s.contains("editar"))name="edit";
        else if(s.contains("categor"))name="folder";
        else if(s.contains("recordatorio")||s.contains("aviso"))name="bell";
        else if(s.contains("repetir"))name="repeat";
        else if(s.contains("calendario"))name="calendar";
        else if(s.contains("buscar"))name="search";
        if(name==null)return;
        OutlineIcon icon=new OutlineIcon(name,b.getCurrentTextColor()==0xffffffff?0xffffffff:BLUE);
        icon.setBounds(0,0,dp(b.getContext(),18),dp(b.getContext(),18));
        b.setCompoundDrawables(icon,null,null,null);b.setCompoundDrawablePadding(dp(b.getContext(),7));
    }
    public static ImageView icon(Activity a,String name,int color,int size){
        ImageView view=new ImageView(a);view.setImageDrawable(new OutlineIcon(name,color));
        view.setContentDescription(name);view.setPadding(dp(a,3),dp(a,3),dp(a,3),dp(a,3));return view;
    }
    public static String statusIcon(String value){
        if(value==null)return "calendar";
        switch(value) {
            case "Agenda":return "check";
            case "Calendario":return "calendar";
            case "Revisar":return "inbox";
            case "Conexiones":return "link";
            default:return "folder";
        }
    }
    /** Drawn directly on Android Canvas to avoid vendor fonts and bitmap scaling. */
    public static final class OutlineIcon extends Drawable {
        private final String name;private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
        private final int ink;
        public OutlineIcon(String name,int color){this.name=name;ink=color;}
        @Override public void draw(Canvas canvas){
            Rect r=getBounds();canvas.save();canvas.translate(r.left,r.top);
            canvas.scale(Math.max(1,r.width())/24f,Math.max(1,r.height())/24f);
            paint.setColor(ink);paint.setStyle(Paint.Style.STROKE);
            paint.setStrokeWidth(1.85f);paint.setStrokeCap(Paint.Cap.ROUND);paint.setStrokeJoin(Paint.Join.ROUND);
            switch(name){
                case "check":
                    canvas.drawRoundRect(4,3,20,21,2,2,paint);line(canvas,8,12,11,15);line(canvas,11,15,17,9);break;
                case "calendar":
                    canvas.drawRoundRect(3,5,21,21,2,2,paint);line(canvas,3,10,21,10);
                    line(canvas,8,2.5f,8,7);line(canvas,16,2.5f,16,7);line(canvas,8,14,10,14);line(canvas,14,14,16,14);break;
                case "bell":
                    Path bell=new Path();bell.moveTo(5,17);bell.lineTo(7,15);bell.lineTo(7,10);
                    bell.cubicTo(7,3,17,3,17,10);bell.lineTo(17,15);bell.lineTo(19,17);bell.close();
                    canvas.drawPath(bell,paint);canvas.drawArc(10,17,14,21,0,180,false,paint);break;
                case "folder":
                    Path folder=new Path();folder.moveTo(2,8);folder.lineTo(2,20);folder.lineTo(22,20);
                    folder.lineTo(22,8);folder.lineTo(11,8);folder.lineTo(8,5);folder.lineTo(2,5);folder.close();
                    canvas.drawPath(folder,paint);break;
                case "clock":
                    canvas.drawCircle(12,12,9,paint);line(canvas,12,7,12,12);line(canvas,12,12,16,14);break;
                case "inbox":
                    Path inbox=new Path();inbox.moveTo(3,5);inbox.lineTo(21,5);inbox.lineTo(21,19);
                    inbox.lineTo(3,19);inbox.close();canvas.drawPath(inbox,paint);
                    line(canvas,3,13,8,13);line(canvas,8,13,10,16);
                    line(canvas,10,16,14,16);line(canvas,14,16,16,13);line(canvas,16,13,21,13);break;
                case "link":
                    canvas.drawRoundRect(1,10,13,18,4,4,paint);
                    canvas.drawRoundRect(11,6,23,14,4,4,paint);line(canvas,8,15,16,9);break;
                case "edit":
                    line(canvas,4,20,9,19);line(canvas,9,19,20,8);
                    line(canvas,20,8,16,4);line(canvas,16,4,5,15);line(canvas,5,15,4,20);break;
                case "trash":
                    canvas.drawRoundRect(6,7,18,21,1.5f,1.5f,paint);line(canvas,4,6,20,6);
                    line(canvas,9,3,15,3);line(canvas,10,11,10,17);line(canvas,14,11,14,17);break;
                case "repeat":
                    canvas.drawArc(3,3,21,21,192,180,false,paint);
                    canvas.drawArc(3,3,21,21,14,166,false,paint);
                    line(canvas,3,6,3,11);line(canvas,3,11,8,11);line(canvas,21,18,21,13);
                    line(canvas,21,13,16,13);break;
                case "search":
                    canvas.drawCircle(10,10,6.5f,paint);line(canvas,15,15,21,21);break;
                case "save":
                    canvas.drawRoundRect(3,3,21,21,2,2,paint);canvas.drawRect(7,3,17,10,paint);
                    canvas.drawRoundRect(7,14,17,21,1,1,paint);break;
                case "gear":
                    canvas.drawCircle(12,12,7,paint);canvas.drawCircle(12,12,2.5f,paint);
                    for(int i=0;i<8;i++){double a=i*Math.PI/4;line(canvas,
                        (float)(12+8*Math.cos(a)),(float)(12+8*Math.sin(a)),
                        (float)(12+10*Math.cos(a)),(float)(12+10*Math.sin(a)));}break;
                case "notes":
                    canvas.drawRoundRect(5,2,19,22,2,2,paint);line(canvas,8,8,16,8);
                    line(canvas,8,12,16,12);line(canvas,8,16,13,16);break;
                case "warning":
                    Path p=new Path();p.moveTo(12,3);p.lineTo(22,21);p.lineTo(2,21);p.close();
                    canvas.drawPath(p,paint);line(canvas,12,9,12,14);canvas.drawCircle(12,17,0.7f,paint);break;
                default:canvas.drawCircle(12,12,9,paint);
            }
            canvas.restore();
        }
        private void line(Canvas c,float a,float b,float x,float y){c.drawLine(a,b,x,y,paint);}
        @Override public void setAlpha(int alpha){paint.setAlpha(alpha);invalidateSelf();}
        @Override public void setColorFilter(ColorFilter filter){paint.setColorFilter(filter);invalidateSelf();}
        @Override public int getOpacity(){return PixelFormat.TRANSLUCENT;}
        @Override public int getIntrinsicWidth(){return 24;}
        @Override public int getIntrinsicHeight(){return 24;}
    }
}
