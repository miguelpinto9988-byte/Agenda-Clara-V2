package pe.agendaclara.app;

import java.util.List;

/** Synthetic pixel tests of pastel course boxes without Android runtime. */
public final class Phase77ColorTests {
    private static void check(boolean value,String label) {
        if(!value)throw new AssertionError(label);
    }
    private static void paint(int[] pixels,int width,int left,int top,
                              int right,int bottom,int color) {
        for(int y=top;y<bottom;y++)for(int x=left;x<right;x++)
            pixels[y*width+x]=color;
    }
    public static void main(String[] args) {
        int width=640,height=500;
        int[] pixels=new int[width*height];
        java.util.Arrays.fill(pixels,0xffffffff);
        paint(pixels,width,165,170,295,260,0xff80b2ed); // blue course tile
        paint(pixels,width,345,170,490,260,0xffabe9c0); // green course tile
        paint(pixels,width,190,193,250,208,0xff182746); // navy course text hole
        paint(pixels,width,185,38,460,62,0xff586cff);  // colorful title: exclude top
        List<ScheduleGridInterpreter.Tile> tiles=
            ScheduleColorTileDetector.detect(pixels,width,height);
        check(tiles.size()==2,"Expect two colored course rectangles, got "+tiles.size());
        check(tiles.get(0).left==165 && tiles.get(0).top==170,
                "Blue course cell coordinates are preserved");
        check(tiles.get(1).left==345&&tiles.get(1).top==170,
                "Green course cell coordinates are preserved");
        paint(pixels,width,100,100,540,440,0xff80b2ed); // huge decorative background
        tiles=ScheduleColorTileDetector.detect(pixels,width,height);
        check(tiles.isEmpty(),"Page-wide colors should not count as courses");
        java.util.Arrays.fill(pixels,0xffffffff);
        check(ScheduleColorTileDetector.detect(pixels,width,height).isEmpty(),
                "Pure white background is not a colored tile");
        System.out.println("PASS OCR 3.13.7: blue/green course cells recognized; header/background rejected");
    }
}
