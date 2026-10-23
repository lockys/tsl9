package dev.tsl9.morphe;

import android.content.Context;
import android.content.res.ColorStateList;
import android.graphics.*;
import android.graphics.drawable.*;
import android.view.*;
import android.widget.*;

/** Shared native visual vocabulary. No device/session state lives here. */
final class AppUi {
    static final int BG=0xfff7f8f5,INK=0xff202a27,MUTED=0xff59655f,TEAL=0xff205c50,
        LINE=0xffd4ded8,SAGE=0xffe1efe9,WHITE=0xffffffff,DISABLED=0xffe7ece8,AMBER=0xff956000;
    static int dp(Context c,float v){return Math.round(v*c.getResources().getDisplayMetrics().density);}
    static GradientDrawable shape(Context c,int color,int radius,int border){
        GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(c,radius));if(border!=0)d.setStroke(dp(c,1),border);return d;
    }
    static TextView text(Context c,String value,int size,int color){
        TextView v=new TextView(c);v.setText(value);v.setTextSize(size);v.setTextColor(color);v.setFontFeatureSettings("tnum");v.setPadding(0,dp(c,4),0,dp(c,4));return v;
    }
    static TextView heading(Context c,String value){TextView v=text(c,value,19,INK);v.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));v.setPadding(0,dp(c,18),0,dp(c,8));return v;}
    static LinearLayout column(Context c){LinearLayout v=new LinearLayout(c);v.setOrientation(LinearLayout.VERTICAL);return v;}
    static LinearLayout page(Context c){LinearLayout v=column(c);v.setPadding(dp(c,20),dp(c,10),dp(c,20),dp(c,24));v.setBackgroundColor(BG);return v;}
    static LinearLayout card(Context c){LinearLayout v=column(c);v.setPadding(dp(c,14),dp(c,12),dp(c,14),dp(c,12));v.setBackground(shape(c,WHITE,16,LINE));return v;}
    static void style(Button b,boolean primary){
        Context c=b.getContext();b.setAllCaps(false);b.setTextSize(15);b.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));b.setMinHeight(dp(c,52));b.setMinimumHeight(dp(c,52));b.setMinWidth(0);b.setMinimumWidth(0);b.setPadding(dp(c,14),dp(c,10),dp(c,14),dp(c,10));
        int[][] states={new int[]{-android.R.attr.state_enabled},new int[0]};
        b.setTextColor(new ColorStateList(states,new int[]{0xff69756e,primary?WHITE:TEAL}));
        StateListDrawable base=new StateListDrawable();base.addState(states[0],shape(c,DISABLED,14,0));base.addState(new int[]{android.R.attr.state_selected},shape(c,SAGE,14,0));base.addState(states[1],shape(c,primary?TEAL:WHITE,14,primary?0:LINE));
        b.setBackground(new RippleDrawable(ColorStateList.valueOf(0x25205c50),base,null));b.setElevation(0);b.setStateListAnimator(null);
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,dp(c,5),0,dp(c,5));b.setLayoutParams(p);
    }
    static void icon(TextView v,String kind){Icon d=new Icon(kind);d.setBounds(0,0,dp(v.getContext(),22),dp(v.getContext(),22));v.setCompoundDrawablesRelative(d,null,null,null);v.setCompoundDrawablePadding(dp(v.getContext(),10));}
    static void row(LinearLayout row,View a,View b){
        Context c=row.getContext();LinearLayout.LayoutParams left=new LinearLayout.LayoutParams(0,-2,1);left.setMarginEnd(dp(c,5));LinearLayout.LayoutParams right=new LinearLayout.LayoutParams(0,-2,1);right.setMarginStart(dp(c,5));row.addView(a,left);row.addView(b,right);
    }
    static TextView tab(Context c,String title,String kind){
        TextView v=text(c,title,12,INK);v.setGravity(Gravity.CENTER);v.setMinHeight(dp(c,64));v.setPadding(dp(c,5),dp(c,7),dp(c,5),dp(c,7));v.setMaxLines(2);v.setContentDescription(title);
        int[][] states={new int[]{android.R.attr.state_selected},new int[0]};v.setTextColor(new ColorStateList(states,new int[]{TEAL,MUTED}));
        StateListDrawable bg=new StateListDrawable();bg.addState(states[0],shape(c,SAGE,999,0));bg.addState(states[1],shape(c,Color.TRANSPARENT,999,0));v.setBackground(new RippleDrawable(ColorStateList.valueOf(0x19205c50),bg,null));
        Icon icon=new Icon(kind,true);icon.setBounds(0,0,dp(c,23),dp(c,23));v.setCompoundDrawables(null,icon,null,null);v.setCompoundDrawablePadding(dp(c,3));return v;
    }
    static LinearLayout disclosure(Context c,LinearLayout parent,String title,LinearLayout detail){
        Button header=new Button(c);header.setText(title);style(header,false);header.setGravity(Gravity.START|Gravity.CENTER_VERTICAL);icon(header,"chevron");
        detail.setVisibility(View.GONE);header.setOnClickListener(v->{boolean open=detail.getVisibility()!=View.VISIBLE;detail.setVisibility(open?View.VISIBLE:View.GONE);header.setSelected(open);});parent.addView(header);parent.addView(detail);return detail;
    }
    static void selected(Button b,boolean selected){b.setSelected(selected);b.setTextColor(selected?TEAL:MUTED);}
    /** Small geometric line icons share a single stroke and state palette. */
    static final class Icon extends Drawable {
        private final String kind;private final boolean navigation;private final Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
        Icon(String kind){this(kind,false);}Icon(String kind,boolean navigation){this.kind=kind;this.navigation=navigation;}
        @Override public int getIntrinsicWidth(){return 24;}
        @Override public int getIntrinsicHeight(){return 24;}
        @Override public boolean isStateful(){return true;}
        @Override protected boolean onStateChange(int[] state){invalidateSelf();return true;}
        private void line(Canvas c,float... xy){Path path=new Path();path.moveTo(xy[0],xy[1]);for(int i=2;i<xy.length;i+=2)path.lineTo(xy[i],xy[i+1]);c.drawPath(path,p);}
        @Override public void draw(Canvas canvas){
            int save=canvas.save();Rect b=getBounds();canvas.translate(b.left,b.top);canvas.scale(b.width()/24f,b.height()/24f);boolean enabled=false,selected=false;for(int s:getState()){if(s==android.R.attr.state_enabled)enabled=true;if(s==android.R.attr.state_selected)selected=true;}p.setColor(!enabled||navigation&&!selected?MUTED:TEAL);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.7f);p.setStrokeCap(Paint.Cap.ROUND);p.setStrokeJoin(Paint.Join.ROUND);
            switch(kind){
                case "bluetooth":line(canvas,7,7,17,16,12,21,12,3,17,8,7,17);break;
                case "car":canvas.drawRoundRect(4,10,20,19,3,3,p);line(canvas,5,10,8,5,16,5,19,10);line(canvas,5,18,5,21);line(canvas,19,18,19,21);line(canvas,7,14,8,14);line(canvas,16,14,17,14);break;
                case "chart":line(canvas,5,20,5,13);line(canvas,12,20,12,4);line(canvas,19,20,19,9);break;
                case "file":line(canvas,14,3,5,3,5,21,19,21,19,8,14,3,14,8,19,8);break;
                case "lock":case "unlock":canvas.drawRoundRect(5,10,19,21,2,2,p);if(kind.equals("lock"))canvas.drawArc(8,2,16,14,180,180,false,p);else canvas.drawArc(8,2,18,14,180,170,false,p);break;
                case "seat":line(canvas,16,4,13,15,6,15,5,19,15,19,20,6);break;
                case "up":line(canvas,5,15,12,8,19,15);break;
                case "down":line(canvas,5,9,12,16,19,9);break;
                case "left":line(canvas,15,5,8,12,15,19);break;
                case "right":case "chevron":line(canvas,9,5,16,12,9,19);break;
                case "refresh":canvas.drawArc(4,4,20,20,30,290,false,p);line(canvas,20,4,20,10,14,10);break;
                case "globe":canvas.drawCircle(12,12,9,p);canvas.drawOval(8,3,16,21,p);line(canvas,3,12,21,12);break;
                case "export":line(canvas,13,4,21,4,21,12);line(canvas,21,4,11,14);line(canvas,9,6,4,6,4,21,19,21,19,16);break;
                default:canvas.drawCircle(12,12,9,p);line(canvas,12,11,12,17);canvas.drawPoint(12,7,p);
            }canvas.restoreToCount(save);
        }
        @Override public void setAlpha(int alpha){p.setAlpha(alpha);}
        @Override public void setColorFilter(ColorFilter f){p.setColorFilter(f);}
        @Override public int getOpacity(){return PixelFormat.TRANSLUCENT;}
    }
}
