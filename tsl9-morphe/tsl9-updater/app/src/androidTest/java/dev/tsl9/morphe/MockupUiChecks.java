package dev.tsl9.morphe;

import android.app.Activity;
import android.view.View;
import android.widget.TabHost;
import android.widget.TabWidget;
import android.widget.TextView;
import java.lang.reflect.Field;

/** Native navigation contract; never scans or connects Bluetooth. */
final class MockupUiChecks {
    private final Activity a;private int checks;
    MockupUiChecks(Activity a){this.a=a;}
    private void check(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
    int run() throws Exception {
        Field f=a.getClass().getDeclaredField("tabs");f.setAccessible(true);TabHost tabs=(TabHost)f.get(a);
        TabWidget bar=tabs.getTabWidget();float density=a.getResources().getDisplayMetrics().density;
        check(bar.getTabCount()==4,"four native navigation destinations include Settings");
        check(bar.getWidth()<tabs.getWidth()-24*density,"pill navigation has visible horizontal breathing room");
        float fontScale=a.getResources().getConfiguration().fontScale;
        if(fontScale<=1.05f&&tabs.getWidth()/density<600){
            check(bar.getWidth()>=tabs.getWidth()*0.50f&&bar.getWidth()<=tabs.getWidth()*0.57f,"compact pill follows reference width around 52 percent");
            check(bar.getWidth()/(float)bar.getHeight()>=3.6f&&bar.getWidth()/(float)bar.getHeight()<=4.5f,"compact pill follows reference aspect near four to one");
        }
        check(Math.abs(bar.getLeft()+bar.getWidth()/2f-tabs.getWidth()/2f)<=2*density,"pill remains horizontally centered");
        for(int i=0;i<4;i++){
            View v=bar.getChildTabViewAt(i);check(v.getHeight()>=48*density,"tab has a touch target at least 48dp high");
            check(v.getWidth()>=48*density,"compact tab keeps a touch target at least 48dp wide");
            check(v instanceof TextView&&!((TextView)v).getText().toString().isEmpty(),"tab retains an accessible localized label");
            check(((TextView)v).getCompoundDrawables()[1]!=null,"each navigation destination has an icon");
            check(((TextView)v).getMaxLines()==1,"compact navigation keeps a single short label line");
            int[] names={R.string.tab_tools,R.string.tab_car,R.string.live_tab,R.string.settings_title};check(a.getString(names[i]).contentEquals(v.getContentDescription()),"short labels preserve full accessible destination names");
            TextView label=(TextView)v;check(label.getPaint().measureText(label.getText().toString())<=v.getWidth()-v.getPaddingLeft()-v.getPaddingRight()+1,"scaled localized navigation label fits its slot");
            v.performClick();check(tabs.getCurrentTab()==i,"native pill tab opens its destination");
        }
        tabs.setCurrentTabByTag("tools");
        tabs.setCurrentTabByTag("settings");Field lf=a.getClass().getDeclaredField("language");lf.setAccessible(true);View language=(View)lf.get(a);check(language.isShown(),"language selector is reachable inside Settings");tabs.setCurrentTabByTag("tools");check(!language.isShown(),"language selector stays out of update content");return checks;
    }
}
