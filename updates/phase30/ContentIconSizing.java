package pe.agendaclara.app;

import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.LinearLayout;

/** Gentle +4dp increase for content PNGs, never applied to the bottom navigation. */
public final class ContentIconSizing {
    private ContentIconSizing(){}
    public static void apply(View root){
        if(root==null)return;
        if(root instanceof ImageView && "content_png_icon".equals(root.getTag())){
            ImageView icon=(ImageView)root;
            ViewGroup.LayoutParams lp=icon.getLayoutParams();
            int dp=UiDesign.dp(icon.getContext(),1);
            if(lp!=null && lp.width>=12*dp && lp.height>=12*dp
                    && lp.width<=64*dp && lp.height<=64*dp){
                lp.width+=4*dp;lp.height+=4*dp;
                if(lp instanceof LinearLayout.LayoutParams && icon.getParent() instanceof LinearLayout){
                    LinearLayout parent=(LinearLayout)icon.getParent();
                    if(parent.getOrientation()==LinearLayout.HORIZONTAL)
                        ((LinearLayout.LayoutParams)lp).rightMargin+=6*dp;
                }
                icon.setPadding(0,0,0,0);
                icon.setLayoutParams(lp);
            }
        }
        if(root instanceof ViewGroup){
            ViewGroup group=(ViewGroup)root;
            for(int i=0;i<group.getChildCount();i++)apply(group.getChildAt(i));
        }
    }
}
