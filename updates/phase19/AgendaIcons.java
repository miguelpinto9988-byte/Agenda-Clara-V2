package pe.agendaclara.app;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.drawable.Drawable;

/** Density-independent custom symbols. All icons are drawn in a 24x24 viewport. */
public final class AgendaIcons {
    private AgendaIcons(){}
    public static final int TASK=0, CALENDAR=1, BELL=2, NOTE=3, IMPORT=4, PEOPLE=5;
    public static Drawable create(int kind,int tint){
        return new Drawable(){
            final Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
            @Override public void draw(Canvas canvas){
                int save=canvas.save();
                android.graphics.Rect b=getBounds();
                canvas.translate(b.left,b.top);
                canvas.scale(b.width()/24f,b.height()/24f);
                p.setColor(tint);p.setStrokeWidth(1.8f);p.setStrokeCap(Paint.Cap.ROUND);
                p.setStrokeJoin(Paint.Join.ROUND);p.setStyle(Paint.Style.STROKE);
                switch(kind){
                    case TASK:
                        canvas.drawRoundRect(new RectF(4,4,20,20),3,3,p);
                        Path check=new Path();check.moveTo(7,12);check.lineTo(10.5f,15.5f);check.lineTo(17,8.5f);
                        canvas.drawPath(check,p);break;
                    case CALENDAR:
                        canvas.drawRoundRect(new RectF(3,5,21,21),3,3,p);
                        canvas.drawLine(3,10,21,10,p);canvas.drawLine(8,3,8,7,p);
                        canvas.drawLine(16,3,16,7,p);canvas.drawCircle(9,14,1,p);
                        canvas.drawCircle(15,14,1,p);break;
                    case BELL:
                        Path bell=new Path();bell.moveTo(5,17);bell.lineTo(7,14);bell.lineTo(7,10);
                        bell.cubicTo(7,3,17,3,17,10);bell.lineTo(17,14);bell.lineTo(19,17);
                        bell.close();canvas.drawPath(bell,p);canvas.drawArc(new RectF(10,17,14,21),0,180,false,p);break;
                    case NOTE:
                        canvas.drawRoundRect(new RectF(5,3,19,21),2,2,p);
                        canvas.drawLine(8,8,16,8,p);canvas.drawLine(8,12,16,12,p);
                        canvas.drawLine(8,16,13,16,p);break;
                    case IMPORT:
                        canvas.drawLine(12,3,12,16,p);canvas.drawLine(7,11,12,16,p);
                        canvas.drawLine(17,11,12,16,p);
                        canvas.drawLine(4,19,20,19,p);canvas.drawLine(4,16,4,19,p);
                        canvas.drawLine(20,16,20,19,p);break;
                    case PEOPLE:
                        canvas.drawCircle(9,8,3,p);
                        canvas.drawArc(new RectF(3,13,15,21),185,170,false,p);
                        canvas.drawArc(new RectF(14,5,21,12),195,150,false,p);
                        canvas.drawArc(new RectF(15,13,23,20),195,135,false,p);break;
                    default: canvas.drawCircle(12,12,7,p);
                }
                canvas.restoreToCount(save);
            }
            @Override public void setAlpha(int alpha){p.setAlpha(alpha);}
            @Override public void setColorFilter(android.graphics.ColorFilter filter){p.setColorFilter(filter);}
            @Override public int getOpacity(){return PixelFormat.TRANSLUCENT;}
        };
    }
}
