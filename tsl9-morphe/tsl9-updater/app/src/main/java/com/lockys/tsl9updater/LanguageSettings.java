package com.lockys.tsl9updater;
import android.app.Activity;
import android.app.LocaleManager;
import android.content.Context;
import android.content.res.Configuration;
import android.os.Build;
import android.os.LocaleList;
import java.util.Locale;
/** Persist explicit choices on every supported Android version; never change system locale. */
final class LanguageSettings {
    private static final String[] TAGS={"","zh-Hans","zh-Hant","en"};
    static int index(Context c){
        String tag;
        if(Build.VERSION.SDK_INT>=33){
            LocaleList locales=c.getSystemService(LocaleManager.class).getApplicationLocales();
            if(locales.isEmpty())return 0;
            Locale locale=normalized(locales.get(0));tag=locale.getLanguage().equals("zh")?"zh-"+locale.getScript():locale.getLanguage();
        }else tag=c.getSharedPreferences("settings",Context.MODE_PRIVATE).getString("language","");
        for(int i=0;i<TAGS.length;i++)if(TAGS[i].equals(tag))return i;return 0;
    }
    static Context wrap(Context c){
        if(Build.VERSION.SDK_INT>=33)return c; // Android owns the system / per-app locale on 33+.
        String tag=TAGS[index(c)];
        Configuration system=android.content.res.Resources.getSystem().getConfiguration();
        Configuration config=new Configuration(c.getResources().getConfiguration());
        if(tag.isEmpty()&&Build.VERSION.SDK_INT>=24){
            LocaleList locales=normalized(system.getLocales());config.setLocales(locales);config.setLayoutDirection(locales.get(0));
        }else{
            Locale locale=normalized(tag.isEmpty()?system.locale:Locale.forLanguageTag(tag));config.setLocale(locale);config.setLayoutDirection(locale);
        }
        return c.createConfigurationContext(config);
    }
    static Locale normalized(Locale locale){
        if(!locale.getLanguage().equals("zh")||!locale.getScript().isEmpty())return locale;
        String country=locale.getCountry();String script=country.equals("TW")||country.equals("HK")||country.equals("MO")?"Hant":"Hans";
        return new Locale.Builder().setLocale(locale).setScript(script).build();
    }
    @android.annotation.TargetApi(24)
    static LocaleList normalized(LocaleList input){
        Locale[] locales=new Locale[input.size()];for(int i=0;i<locales.length;i++)locales[i]=normalized(input.get(i));return new LocaleList(locales);
    }
    static void select(Activity a,int index){
        if(index<0||index>=TAGS.length)throw new IllegalArgumentException("Invalid language index");
        String tag=TAGS[index];
        // Commit before recreation so attachBaseContext always sees the new choice.
        if(!a.getSharedPreferences("settings",Context.MODE_PRIVATE).edit().putString("language",tag).commit())return;
        if(Build.VERSION.SDK_INT>=33){
            LocaleManager manager=a.getSystemService(LocaleManager.class);
            LocaleList locales=tag.isEmpty()?LocaleList.getEmptyLocaleList():LocaleList.forLanguageTags(tag);
            boolean changed=!manager.getApplicationLocales().equals(locales);manager.setApplicationLocales(locales);
            if(!changed)a.recreate();
        }else a.recreate();
    }
}
