package pe.agendaclara.app;

import java.util.*;

/**
 * Detects pastel/saturated timetable tiles when the white-tile detector misses them.
 * Pure Java: receives downsampled ARGB pixels; no network, ML or Android dependencies.
 * Layout rules reject colored titles, legends, tiny icons and page-wide backgrounds.
 */
public final class ScheduleColorTileDetector {
    private ScheduleColorTileDetector(){}
    private static boolean colored(int argb) {
        int r=(argb>>>16)&255,g=(argb>>>8)&255,b=argb&255;
        int max=Math.max(r,Math.max(g,b)),min=Math.min(r,Math.min(g,b));
        return max>=155&&min>=65&&max-min>=27;
    }
    private static int enqueue(int pos,int[] pixels,byte[] seen,int[] queue,int tail) {
        if(seen[pos]!=0)return tail;
        seen[pos]=1;
        if(colored(pixels[pos]))queue[tail++]=pos;
        return tail;
    }
    public static List<ScheduleGridInterpreter.Tile> detect(int[] pixels,int width,int height) {
        ArrayList<ScheduleGridInterpreter.Tile> result=new ArrayList<>();
        if(pixels==null||width<120||height<120||
                (long)width*height>2000000||pixels.length<(long)width*height)return result;
        int count=width*height;
        byte[] seen=new byte[count];
        int[] queue=new int[count];
        int minWidth=Math.max(28,width/23),minHeight=Math.max(15,height/30);
        for(int start=0;start<count;start++){
            if(seen[start]!=0)continue;
            seen[start]=1;
            if(!colored(pixels[start]))continue;
            int first=start%width,last=first,top=start/width,bottom=top;
            int head=0,tail=1;queue[0]=start;
            while(head<tail){
                int pixel=queue[head++],x=pixel%width,y=pixel/width;
                first=Math.min(first,x);last=Math.max(last,x);
                top=Math.min(top,y);bottom=Math.max(bottom,y);
                if(x>0)tail=enqueue(pixel-1,pixels,seen,queue,tail);
                if(x+1<width)tail=enqueue(pixel+1,pixels,seen,queue,tail);
                if(y>0)tail=enqueue(pixel-width,pixels,seen,queue,tail);
                if(y+1<height)tail=enqueue(pixel+width,pixels,seen,queue,tail);
            }
            int w=last-first+1,h=bottom-top+1;
            if(w<minWidth||h<minHeight||w>width*.56||h>height*.67||
                    first<width*.105||top<height*.13)continue;
            // Text creates holes. The colored portion should still occupy a tile.
            if((double)tail/(w*h)<.54)continue;
            result.add(new ScheduleGridInterpreter.Tile(first,top,last+1,bottom+1));
            if(result.size()>=100)break;
        }
        result.sort(Comparator.comparingInt((ScheduleGridInterpreter.Tile x)->x.top)
                              .thenComparingInt(x->x.left));
        return result;
    }
}
