package pe.agendaclara.app;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.LinearGradient;
import android.graphics.RadialGradient;
import android.graphics.Shader;
import android.graphics.Color;
import android.graphics.Path;
import android.graphics.RectF;
import android.graphics.drawable.Drawable;
import android.view.View;
import android.graphics.PixelFormat;

/** Lightweight offline drawing toolkit shared by native Java screens. */
public final class AgendaDraw {
    private AgendaDraw(){}
    public static final int BLUE=0xff2765f5, BLUE_LIGHT=0xff6fb5ff, INK=0xff182b52;
    public static Drawable gradientCard(int radiusDp, Context context){
        float d=context.getResources().getDisplayMetrics().density;
        return new Drawable(){
            final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
            @Override public void draw(Canvas canvas){
                RectF r=new RectF(getBounds());
                paint.setShader(new LinearGradient(0,0,r.width(),r.height(),
                    new int[]{Color.WHITE,0xfff4f8ff,0xffeaf2ff},null,Shader.TileMode.CLAMP));
                canvas.drawRoundRect(r,radiusDp*d,radiusDp*d,paint);
                paint.setShader(null);paint.setStyle(Paint.Style.STROKE);
                paint.setStrokeWidth(d);paint.setColor(0xffd9e6fc);
                canvas.drawRoundRect(new RectF(d/2,d/2,r.right-d/2,r.bottom-d/2),
                    radiusDp*d,radiusDp*d,paint);
                paint.setStyle(Paint.Style.FILL);
            }
            @Override public void setAlpha(int alpha){paint.setAlpha(alpha);}
            @Override public void setColorFilter(android.graphics.ColorFilter filter){paint.setColorFilter(filter);}
            @Override public int getOpacity(){return PixelFormat.TRANSLUCENT;}
        };
    }
    public static Drawable luminousButton(Context context){
        return new Drawable(){
            final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
            @Override public void draw(Canvas canvas){
                float w=getBounds().width(),h=getBounds().height();
                float cx=w/2f,cy=h/2f,r=Math.min(w,h)*.42f;
                paint.setShader(new RadialGradient(cx,cy,Math.min(w,h)*.5f,
                    new int[]{0x662b83ff,0x222b83ff,Color.TRANSPARENT},
                    new float[]{0f,.65f,1f},Shader.TileMode.CLAMP));
                canvas.drawCircle(cx,cy,Math.min(w,h)*.5f,paint);
                paint.setShader(new LinearGradient(0,0,w,h,
                    new int[]{0xff69b4ff,BLUE,0xff1841cb},null,Shader.TileMode.CLAMP));
                canvas.drawCircle(cx,cy,r,paint);
                paint.setShader(null);paint.setColor(0x88ffffff);
                paint.setStrokeWidth(Math.max(1f,w*.025f));paint.setStyle(Paint.Style.STROKE);
                canvas.drawCircle(cx,cy,r*.89f,paint);paint.setStyle(Paint.Style.FILL);
                paint.setColor(Color.WHITE);paint.setStrokeCap(Paint.Cap.ROUND);
                paint.setStrokeWidth(Math.max(2f,w*.065f));
                canvas.drawLine(cx-r*.36f,cy,cx+r*.36f,cy,paint);
                canvas.drawLine(cx,cy-r*.36f,cx,cy+r*.36f,paint);
            }
            @Override public void setAlpha(int alpha){paint.setAlpha(alpha);}
            @Override public void setColorFilter(android.graphics.ColorFilter filter){paint.setColorFilter(filter);}
            @Override public int getOpacity(){return PixelFormat.TRANSLUCENT;}
        };
    }
    public static Drawable categoryGlyph(int color){
        return new Drawable(){
            final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
            @Override public void draw(Canvas canvas){
                float w=getBounds().width(),h=getBounds().height(),d=Math.min(w,h);
                paint.setColor((color&0x00ffffff)|0x22000000);
                canvas.drawCircle(w/2f,h/2f,d*.47f,paint);
                paint.setColor(color);paint.setStrokeWidth(d*.07f);
                paint.setStyle(Paint.Style.STROKE);paint.setStrokeCap(Paint.Cap.ROUND);
                RectF rect=new RectF(w*.29f,h*.28f,w*.71f,h*.73f);
                canvas.drawRoundRect(rect,d*.07f,d*.07f,paint);
                canvas.drawLine(w*.38f,h*.42f,w*.62f,h*.42f,paint);
                canvas.drawLine(w*.38f,h*.54f,w*.57f,h*.54f,paint);
                paint.setStyle(Paint.Style.FILL);
            }
            @Override public void setAlpha(int alpha){paint.setAlpha(alpha);}
            @Override public void setColorFilter(android.graphics.ColorFilter filter){paint.setColorFilter(filter);}
            @Override public int getOpacity(){return PixelFormat.TRANSLUCENT;}
        };
    }
}
