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
        check(bar.getTabCount()==3,"three native navigation destinations retained");
        check(bar.getWidth()<tabs.getWidth()-24*density,"pill navigation has visible horizontal breathing room");
        for(int i=0;i<3;i++){
            View v=bar.getChildTabViewAt(i);check(v.getHeight()>=48*density,"tab has a touch target at least 48dp high");
            check(v instanceof TextView&&!((TextView)v).getText().toString().isEmpty(),"tab retains an accessible localized label");
            check(((TextView)v).getCompoundDrawables()[1]!=null,"each navigation destination has an icon");
            v.performClick();check(tabs.getCurrentTab()==i,"native pill tab opens its destination");
        }
        tabs.setCurrentTabByTag("tools");
        Field lf=a.getClass().getDeclaredField("languageButton"),pf=a.getClass().getDeclaredField("languagePanel");lf.setAccessible(true);pf.setAccessible(true);
        View language=(View)lf.get(a),panel=(View)pf.get(a);language.performClick();check(panel.getVisibility()==View.VISIBLE,"language action reveals the native selector");language.performClick();check(panel.getVisibility()==View.GONE,"language action dismisses its selector");return checks;
    }
}
