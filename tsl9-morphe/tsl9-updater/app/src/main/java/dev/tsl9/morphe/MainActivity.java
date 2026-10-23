package dev.tsl9.morphe;

import android.Manifest;
import android.app.*;
import android.bluetooth.*;
import android.content.*;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.graphics.Color;
import android.os.*;
import android.provider.OpenableColumns;
import android.text.InputType;
import android.view.*;
import android.widget.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.*;

/** Companion test APK; no INTERNET permission, no server credentials or firmware assets. */
public final class MainActivity extends Activity implements BleClient.Events,OtaSession.Listener {
    private final Handler handler=new Handler(Looper.getMainLooper());
    private BleClient ble;private OtaSession ota;private BluetoothDevice selected;private int reconnects;
    private VehicleControls car;private TabHost tabs;private CheckBox lightLayout;private LiveVehicleData liveData;private LivePanel livePanel;
    private TextView versionView,carVersionView,carReadiness,carStatus;private DeviceInfoSnapshot versionInfo;
    private Button pressedSeat,versionButton,carVersionButton,carRefreshButton,seatStop,lightOn,lightOff;private long lastCarPoll,lastCarInfoPoll;private boolean closeVehicleAfterStop;private String lastCarGate="";
    private final ArrayList<Button> carButtons=new ArrayList<>();
    private LinearLayout captureDetails,languagePanel,driverPad,passengerPad;private TextView headerConnection;private Button languageButton,driverSelector,passengerSelector;private int selectedSeat;
    private HardwareCapture hardware;private boolean captureStopping,disconnectAfterCaptureStop,canStreaming,hardwareSession,hardwareDirty,hardwareScheduled;
    private File hardwareFile;private String previousHardware="";private TextView hardwareStatus,hardwareView;
    private String displayedLocale;private boolean pendingLanguageRefresh;private Spinner language;private Spinner captureMode;private EditText canIds;private CheckBox canData;
    private Button captureStart,captureStop,hardwareExport;
    private byte[] info;private FirmwareImage image;private byte[] selectedBytes;private String imageName="";
    private boolean passwordAccepted,passwordRequired,destroyed,leaving;private TextView status,deviceInfo,fileInfo,logView,stage;
    private Button scanButton,disconnectButton,readButton,passwordButton,fileButton,flashButton,cancelButton,exportButton;
    private long lastBootPoll;
    private LinearLayout deviceList;private Spinner format;private ProgressBar progress;private CheckBox match,hw20;
    private final LinkedHashMap<String,BluetoothDevice> devices=new LinkedHashMap<>();
    private final StringBuilder logs=new StringBuilder();private File logFile;private boolean logDirty,logScheduled;
    private static final int GREEN=AppUi.TEAL,DARK=AppUi.INK,MUTED=AppUi.MUTED;
    @Override protected void attachBaseContext(Context base){super.attachBaseContext(LanguageSettings.wrap(base));}
    private String s(int id,Object... args){return getString(id,args);}
    private String message(UiMessage detail){return UiStrings.render(this,detail);}
    @Override public void onCreate(Bundle b){
        super.onCreate(b);getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR|(Build.VERSION.SDK_INT>=26?View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR:0));ota=new OtaSession(this,SystemClock::elapsedRealtime);ble=new BleClient(this,this);hardware=new HardwareCapture(SystemClock::elapsedRealtime);liveData=new LiveVehicleData(SystemClock::elapsedRealtime);
        car=new VehicleControls(new VehicleControls.Listener(){
            public void send(int command,byte[] payload,Runnable written){ble.send(command,payload,written);}
            public void sendGuarded(int command,byte[] payload,Runnable written,VehicleControls.WriteGuard guard){ble.sendGuarded(command,payload,written,guard);}
            public void changed(UiMessage detail){carChanged(detail);}
            public void log(String value){MainActivity.this.log(value);}
        },SystemClock::elapsedRealtime);
        hardwareFile=new File(getFilesDir(),"latest-hardware.jsonl");if(hardwareFile.length()<2*1024*1024){try{previousHardware=new String(readLimited(new android.util.AtomicFile(hardwareFile).openRead(),2*1024*1024),StandardCharsets.UTF_8);}catch(IOException ignored){}}
        logFile=new File(getFilesDir(),"latest-debug.log");
        if(logFile.exists()&&logFile.length()<256*1024){try{logs.append(new String(readLimited(new FileInputStream(logFile),256*1024),StandardCharsets.UTF_8));}catch(IOException ignored){}}
        displayedLocale=localeSignature(getResources().getConfiguration());buildUi();log("APP v0.7.0-test Android="+Build.VERSION.SDK_INT+" target=TSL9 OEM APP OTA + direct body-controls + live receive-only dashboard");
        if(b!=null){selectSeat(b.getInt("seat",0));if(b.getString("tab")!=null)tabs.setCurrentTabByTag(b.getString("tab"));}handler.post(ticker);refresh();
    }
    private int dp(float n){return Math.round(n*getResources().getDisplayMetrics().density);}
    private TextView text(String value,int size,int color){return AppUi.text(this,value,size,color);}
    private Button button(String title,Runnable run){Button b=new Button(this);b.setText(title);AppUi.style(b,false);b.setOnClickListener(v->{try{run.run();}catch(SecurityException e){state(s(R.string.nearby_permission));log("PERMISSION operation blocked");}catch(IllegalArgumentException e){state(UiStrings.error(this,e));log("VALIDATION "+e.getMessage());}});return b;}
    private TextView tabIndicator(int label,String icon){return AppUi.tab(this,s(label),icon);}
    private void title(LinearLayout body,int title,int subtitle){TextView h=text(s(title),27,DARK);h.setTypeface(android.graphics.Typeface.create("sans-serif-medium",android.graphics.Typeface.NORMAL));body.addView(h);body.addView(text(s(subtitle),14,MUTED));}
    private void section(LinearLayout body,int label){body.addView(AppUi.heading(this,s(label)));}
    private void buildUi(){
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);LinearLayout body=AppUi.page(this);scroll.addView(body);
        title(body,R.string.ui_tools_title,R.string.ui_tools_subtitle);
        if(imageName.isEmpty())imageName=s(R.string.no_bin);
        LinearLayout device=AppUi.card(this);LinearLayout.LayoutParams deviceParams=new LinearLayout.LayoutParams(-1,-2);deviceParams.topMargin=dp(18);body.addView(device,deviceParams);
        TextView module=text("TSL9",20,DARK);AppUi.icon(module,"bluetooth");module.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);device.addView(module);
        status=text(s(R.string.disconnected),14,GREEN);status.setContentDescription(s(R.string.connection_status));device.addView(status);
        LinearLayout row=new LinearLayout(this);scanButton=button(s(R.string.scan),this::scan);AppUi.style(scanButton,true);disconnectButton=button(s(R.string.disconnect),this::disconnectRequested);AppUi.row(row,scanButton,disconnectButton);device.addView(row);
        deviceList=AppUi.column(this);device.addView(deviceList);
        versionView=text(s(R.string.version_not_read),13,MUTED);versionView.setTextIsSelectable(true);device.addView(versionView);
        versionButton=button(s(R.string.version_read),this::requestInfo);AppUi.icon(versionButton,"refresh");device.addView(versionButton);
        LinearLayout moduleDetails=AppUi.column(this);deviceInfo=text(s(R.string.info_hint),13,MUTED);moduleDetails.addView(deviceInfo);
        readButton=button(s(R.string.read_info),this::requestInfo);passwordButton=button(s(R.string.password),this::passwordDialog);moduleDetails.addView(readButton);moduleDetails.addView(passwordButton);
        AppUi.disclosure(this,device,s(R.string.ui_module_details),moduleDetails);
        section(body,R.string.firmware_title);
        fileButton=button(s(R.string.pick_bin),()->{Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/octet-stream");i.putExtra(Intent.EXTRA_MIME_TYPES,new String[]{"application/octet-stream","application/x-binary","*/*"});startActivityForResult(i,100);});AppUi.icon(fileButton,"file");body.addView(fileButton);
        fileInfo=text(imageName,13,MUTED);fileInfo.setTextIsSelectable(true);body.addView(fileInfo);
        format=new Spinner(this);format.setAdapter(new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,new String[]{s(R.string.format_paged),s(R.string.format_raw),s(R.string.format_pad)}));format.setContentDescription(s(R.string.format));format.setMinimumHeight(dp(52));
        format.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener(){public void onNothingSelected(AdapterView<?> p){}public void onItemSelected(AdapterView<?> p,View v,int pos,long id){if(selectedBytes!=null)parseSelected();}});body.addView(format);
        body.addView(text(s(R.string.ui_app_only),13,MUTED));
        LinearLayout advanced=AppUi.column(this);advanced.addView(text(s(R.string.firmware_help),14,MUTED));advanced.addView(text(s(R.string.ota_help),13,MUTED));
        hw20=new CheckBox(this);hw20.setText(s(R.string.hw20));hw20.setOnCheckedChangeListener((b,on)->{if(match!=null)match.setChecked(false);refresh();});advanced.addView(hw20);advanced.addView(text(s(R.string.hw20_help),13,MUTED));AppUi.disclosure(this,body,s(R.string.ui_advanced),advanced);
        match=new CheckBox(this);match.setText(s(R.string.compatibility));match.setTextSize(14);body.addView(match);match.setOnCheckedChangeListener((b,on)->refresh());
        flashButton=button(s(R.string.flash),this::confirmFlash);AppUi.style(flashButton,true);body.addView(flashButton);
        stage=text(s(R.string.waiting),14,GREEN);body.addView(stage);progress=new ProgressBar(this,null,android.R.attr.progressBarStyleHorizontal);progress.setMax(100);body.addView(progress);
        cancelButton=button(s(R.string.stop),()->{ota.cancel(s(R.string.user_stop));ble.close();clearIdentity();state(s(R.string.stopped));});body.addView(cancelButton);
        captureDetails=AppUi.column(this);
        captureMode=new Spinner(this);captureMode.setAdapter(new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,new String[]{s(R.string.mode_ble),s(R.string.mode_can),s(R.string.mode_text)}));captureMode.setContentDescription(s(R.string.capture_mode));captureMode.setMinimumHeight(dp(48));captureDetails.addView(captureMode);
        canIds=new EditText(this);canIds.setSingleLine(true);canIds.setHint(s(R.string.can_ids));canIds.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);canIds.setMinimumHeight(dp(48));captureDetails.addView(canIds);
        canData=new CheckBox(this);canData.setText(s(R.string.can_data));captureDetails.addView(canData);captureDetails.addView(text(s(R.string.capture_help),13,MUTED));
        captureStart=button(s(R.string.capture_start),this::startHardware);captureStop=button(s(R.string.capture_stop),()->stopHardware("manual",false));captureDetails.addView(captureStart);captureDetails.addView(captureStop);
        hardwareStatus=text(previousHardware.isEmpty()?s(R.string.no_capture):s(R.string.previous_capture),14,GREEN);captureDetails.addView(hardwareStatus);
        hardwareExport=button(s(R.string.hardware_export),()->{flushHardware();Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/x-ndjson");i.putExtra(Intent.EXTRA_TITLE,"tsl9-hardware-"+new SimpleDateFormat("yyyyMMdd-HHmmss",Locale.ROOT).format(new Date())+".jsonl");startActivityForResult(i,102);});captureDetails.addView(hardwareExport);
        hardwareView=text("",12,MUTED);hardwareView.setTypeface(android.graphics.Typeface.MONOSPACE);hardwareView.setTextIsSelectable(true);captureDetails.addView(hardwareView);
        section(body,R.string.ui_diagnostics);AppUi.disclosure(this,body,s(R.string.capture_title),captureDetails);
        LinearLayout debugDetails=AppUi.column(this);debugDetails.addView(text(s(R.string.debug_help),13,MUTED));logView=text("",12,MUTED);logView.setTypeface(android.graphics.Typeface.MONOSPACE);logView.setTextIsSelectable(true);debugDetails.addView(logView);AppUi.disclosure(this,body,s(R.string.debug_title),debugDetails);
        exportButton=button(s(R.string.debug_export),()->{flushLog();Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("text/plain");i.putExtra(Intent.EXTRA_TITLE,"tsl9-debug-"+new SimpleDateFormat("yyyyMMdd-HHmmss",Locale.ROOT).format(new Date())+".txt");startActivityForResult(i,101);});AppUi.icon(exportButton,"export");body.addView(exportButton);
        tabs=new TabHost(this);tabs.setId(android.R.id.tabhost);tabs.setBackgroundColor(AppUi.BG);
        LinearLayout tabBody=AppUi.column(this);
        LinearLayout header=new LinearLayout(this);header.setGravity(Gravity.CENTER_VERTICAL);header.setPadding(dp(20),dp(6),dp(20),dp(2));TextView brand=text("TSL9",22,DARK);brand.setContentDescription(s(R.string.app_name));brand.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);header.addView(brand,new LinearLayout.LayoutParams(0,-2,1));
        headerConnection=text(s(R.string.disconnected),12,MUTED);header.addView(headerConnection);
        languageButton=button("",()->languagePanel.setVisibility(languagePanel.getVisibility()==View.VISIBLE?View.GONE:View.VISIBLE));languageButton.setContentDescription(s(R.string.language));AppUi.icon(languageButton,"globe");languageButton.setPadding(dp(12),dp(10),dp(12),dp(10));header.addView(languageButton,new LinearLayout.LayoutParams(dp(48),dp(48)));tabBody.addView(header);
        languagePanel=AppUi.column(this);languagePanel.setPadding(dp(20),0,dp(20),dp(8));languagePanel.addView(text(s(R.string.language),14,MUTED));
        language=new Spinner(this);language.setContentDescription(s(R.string.language));language.setMinimumHeight(dp(48));language.setAdapter(new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,new String[]{s(R.string.system_language),"简体中文","繁體中文","English"}));language.setSelection(LanguageSettings.index(this));
        language.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener(){public void onNothingSelected(AdapterView<?> p){}public void onItemSelected(AdapterView<?> p,View v,int position,long id){if(position==LanguageSettings.index(MainActivity.this))return;if(!canChangeLanguage()){language.setSelection(LanguageSettings.index(MainActivity.this));return;}LanguageSettings.select(MainActivity.this,position);}});
        languagePanel.addView(language);languagePanel.setVisibility(View.GONE);tabBody.addView(languagePanel);
        FrameLayout content=new FrameLayout(this);content.setId(android.R.id.tabcontent);tabBody.addView(content,new LinearLayout.LayoutParams(-1,0,1));
        TabWidget tabBar=new TabWidget(this);tabBar.setId(android.R.id.tabs);tabBar.setStripEnabled(false);tabBar.setPadding(dp(5),dp(4),dp(5),dp(4));tabBar.setBackground(AppUi.shape(this,AppUi.WHITE,999,0));tabBar.setElevation(dp(5));tabBar.setClipToOutline(true);
        LinearLayout.LayoutParams barParams=new LinearLayout.LayoutParams(-1,-2);barParams.setMargins(dp(20),dp(6),dp(20),dp(12));tabBody.addView(tabBar,barParams);tabs.addView(tabBody);tabs.setup();
        ScrollView vehicleScroll=buildVehicleUi();
        livePanel=new LivePanel(this,new LivePanel.Host(){public void query(){requestCarStatus();}public void startCan(String filter){startLiveCan(filter);}public void stopCan(){if(hardware.active()&&hardware.mode()==HardwareCapture.Mode.CAN)stopHardware("manual",false);}public void export(){if(hardwareExport.isEnabled())hardwareExport.performClick();}});
        tabs.addTab(tabs.newTabSpec("tools").setIndicator(tabIndicator(R.string.tab_tools,"bluetooth")).setContent(tag->scroll));tabs.addTab(tabs.newTabSpec("car").setIndicator(tabIndicator(R.string.tab_car,"car")).setContent(tag->vehicleScroll));tabs.addTab(tabs.newTabSpec("live").setIndicator(tabIndicator(R.string.live_tab,"chart")).setContent(tag->livePanel.view));
        tabs.setOnTabChangedListener(tag->{if(!tag.equals("car"))car.stopSeat();if(tag.equals("car")||tag.equals("live")){lastCarPoll=0;lastCarInfoPoll=0;}refresh();});setContentView(tabs);
        tabBody.setOnApplyWindowInsetsListener((v,insets)->{tabBody.setPadding(insets.getSystemWindowInsetLeft(),insets.getSystemWindowInsetTop(),insets.getSystemWindowInsetRight(),insets.getSystemWindowInsetBottom());return insets.consumeSystemWindowInsets();});
    }

    private boolean carTabVisible(){return tabs!=null&&"car".equals(tabs.getCurrentTabTag());}
    private boolean telemetryTabVisible(){return tabs!=null&&(carTabVisible()||"live".equals(tabs.getCurrentTabTag()));}
    private boolean canReadVehicle(){return !leaving&&ble.idle()&&!car.active()&&!ota.active()&&!captureStopping&&info!=null&&(info[3]&1)!=0&&(!passwordRequired||passwordAccepted)&&(!hardware.active()||hardware.mode()!=HardwareCapture.Mode.TEXT);}
    private boolean carReady(){return !leaving&&carTabVisible()&&car.canOperate();}
    private void putText(TextView view,String value){if(view!=null&&!value.contentEquals(view.getText()))view.setText(value);}
    private void displayVersions(){
        String value=s(R.string.version_not_read);
        if(versionInfo!=null)value=s(R.string.version_details,versionInfo.applicationPrefix(),versionInfo.applicationByte,versionInfo.bluetoothPrefix(),versionInfo.bluetoothByte,versionInfo.normalMode?s(R.string.run_mode):s(R.string.boot_mode),new SimpleDateFormat("HH:mm:ss",Locale.ROOT).format(new Date()));
        putText(versionView,versionInfo==null?value:s(R.string.ui_versions_short,versionInfo.applicationPrefix(),versionInfo.bluetoothPrefix(),s(versionInfo.normalMode?R.string.run_mode:R.string.boot_mode)));putText(carVersionView,value);
    }
    private void disconnectRequested(){
        if(car.active()){closeVehicleAfterStop=true;car.cancel();if(car.active()){state(s(R.string.car_seat_stopping));return;}}
        ota.cancel(s(R.string.user_disconnect));stopHardware("user_disconnect",true);if(!captureStopping)ble.close();clearIdentity();selected=null;state(s(R.string.disconnecting));
    }
    private void carChanged(UiMessage detail){
        log("CAR STATE "+detail);if(!destroyed)putText(carStatus,message(detail));
        if(closeVehicleAfterStop&&!car.active()){closeVehicleAfterStop=false;ble.close();if(!destroyed)clearIdentity();}
        if(!destroyed)refresh();
    }
    private void pollCar(){
        if(!telemetryTabVisible()||!canReadVehicle())return;
        long now=SystemClock.elapsedRealtime();
        if(now-lastCarInfoPoll>=5000){requestInfo();return;}
        if(now-lastCarPoll>=1000)requestCarStatus();
    }
    private void requestCarStatus(){
        if(!telemetryTabVisible()||!canReadVehicle())return;
        lastCarPoll=SystemClock.elapsedRealtime();log("CAR STATUS request B0 bytes=1");ble.send(0xb0,new byte[]{1},()->refresh());
    }
    private ScrollView buildVehicleUi(){
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);LinearLayout body=AppUi.page(this);scroll.addView(body);title(body,R.string.car_title,R.string.car_model);
        ImageView vehicleArt=new ImageView(this);vehicleArt.setImageResource(R.drawable.vehicle_profile);vehicleArt.setScaleType(ImageView.ScaleType.FIT_CENTER);vehicleArt.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);body.addView(vehicleArt,new LinearLayout.LayoutParams(-1,dp(88)));
        carReadiness=text(s(R.string.car_telemetry_unknown),14,GREEN);body.addView(carReadiness);
        section(body,R.string.car_locks);LinearLayout locks=new LinearLayout(this);Button lock=button(s(R.string.car_lock),()->sendCar(VehicleControls.Action.LOCK)),unlock=button(s(R.string.car_unlock),()->sendCar(VehicleControls.Action.UNLOCK));AppUi.icon(lock,"lock");AppUi.icon(unlock,"unlock");carButtons.add(lock);carButtons.add(unlock);AppUi.row(locks,lock,unlock);body.addView(locks);
        section(body,R.string.ui_seat);LinearLayout selectors=new LinearLayout(this);
        driverSelector=button(s(R.string.ui_driver),()->selectSeat(0));passengerSelector=button(s(R.string.ui_passenger),()->selectSeat(1));AppUi.row(selectors,driverSelector,passengerSelector);body.addView(selectors);
        driverPad=seatRow(new VehicleControls.Action[]{VehicleControls.Action.DRIVER_LEFT,VehicleControls.Action.DRIVER_RIGHT,VehicleControls.Action.DRIVER_UP,VehicleControls.Action.DRIVER_DOWN});
        passengerPad=seatRow(new VehicleControls.Action[]{VehicleControls.Action.PASSENGER_LEFT,VehicleControls.Action.PASSENGER_RIGHT,VehicleControls.Action.PASSENGER_UP,VehicleControls.Action.PASSENGER_DOWN});body.addView(driverPad);body.addView(passengerPad);selectSeat(0);
        body.addView(text(s(R.string.ui_seat_hint),13,MUTED));seatStop=button(s(R.string.car_stop_seat),()->car.stopSeat());body.addView(seatStop);carStatus=text(s(R.string.car_idle),13,GREEN);body.addView(carStatus);
        LinearLayout lighting=AppUi.column(this);lightLayout=new CheckBox(this);lightLayout.setText(s(R.string.car_light_layout));lightLayout.setOnCheckedChangeListener((v,on)->refresh());lighting.addView(lightLayout);lighting.addView(text(s(R.string.car_light_help),13,MUTED));
        lightOn=button(s(R.string.car_light_on),()->confirmLight(true));lightOff=button(s(R.string.car_light_off),()->confirmLight(false));lighting.addView(lightOn);lighting.addView(lightOff);AppUi.disclosure(this,body,s(R.string.car_lights),lighting);
        body.addView(text(s(R.string.car_help),13,MUTED));
        LinearLayout details=AppUi.column(this);details.addView(text(s(R.string.car_seat_help),13,MUTED));details.addView(button(s(R.string.car_connect_tab),()->tabs.setCurrentTabByTag("tools")));carVersionButton=button(s(R.string.version_read),this::requestInfo);details.addView(carVersionButton);carVersionView=text(s(R.string.version_not_read),13,MUTED);carVersionView.setTextIsSelectable(true);details.addView(carVersionView);carRefreshButton=button(s(R.string.car_read_status),this::requestCarStatus);details.addView(carRefreshButton);AppUi.disclosure(this,body,s(R.string.ui_module_details),details);return scroll;
    }
    private void selectSeat(int selected){
        car.stopSeat();pressedSeat=null;selectedSeat=selected;
        if(driverPad!=null)driverPad.setVisibility(selected==0?View.VISIBLE:View.GONE);if(passengerPad!=null)passengerPad.setVisibility(selected==1?View.VISIBLE:View.GONE);
        AppUi.selected(driverSelector,selected==0);AppUi.selected(passengerSelector,selected==1);
    }
    private LinearLayout seatRow(VehicleControls.Action[] actions){
        LinearLayout pad=AppUi.column(this);String[] arrows={"←","→","↑","↓"},icons={"left","right","up","down"};Button[] buttons=new Button[4];
        for(int i=0;i<actions.length;i++){
            final VehicleControls.Action action=actions[i];final boolean[] touchClick={false};Button b=button("",()->{if(!touchClick[0]&&carReady()&&car.beginSeat(action))handler.postDelayed(()->car.stopSeat(),200);});
            AppUi.Icon icon=new AppUi.Icon(icons[i]);icon.setBounds(0,0,dp(24),dp(24));b.setCompoundDrawables(null,icon,null,null);b.setGravity(Gravity.CENTER);
            b.setContentDescription(s(R.string.car_seat_direction,s(action.name().startsWith("DRIVER")?R.string.car_driver:R.string.car_passenger),arrows[i]));
            b.setOnTouchListener((v,event)->{
                switch(event.getActionMasked()){
                    case MotionEvent.ACTION_DOWN:if(!carReady())return true;pressedSeat=(Button)v;v.setPressed(true);if(!car.beginSeat(action))pressedSeat=null;return true;
                    case MotionEvent.ACTION_MOVE:if(event.getX()<0||event.getY()<0||event.getX()>v.getWidth()||event.getY()>v.getHeight()){v.setPressed(false);car.stopSeat();}return true;
                    case MotionEvent.ACTION_UP:v.setPressed(false);car.stopSeat();touchClick[0]=true;try{v.performClick();}finally{touchClick[0]=false;}return true;
                    case MotionEvent.ACTION_CANCEL:case MotionEvent.ACTION_POINTER_DOWN:v.setPressed(false);car.stopSeat();return true;
                    default:return true;
                }
            });carButtons.add(b);buttons[i]=b;
        }
        for(int r=0;r<3;r++){
            LinearLayout row=new LinearLayout(this);row.setGravity(Gravity.CENTER);pad.addView(row);
            for(int col=0;col<3;col++){
                View child=r==0&&col==1?buttons[2]:r==1&&col==0?buttons[0]:r==1&&col==2?buttons[1]:r==2&&col==1?buttons[3]:new View(this);
                if(r==1&&col==1){ImageView seat=new ImageView(this);seat.setImageDrawable(new AppUi.Icon("seat"));seat.setPadding(dp(18),dp(12),dp(18),dp(12));seat.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);child=seat;}
                LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,dp(48),1);p.setMargins(dp(4),dp(2),dp(4),dp(2));row.addView(child,p);
            }
        }return pad;
    }
    private void sendCar(VehicleControls.Action action){if(carReady())car.perform(action);}
    private void confirmLight(boolean enabled){
        if(!carReady()||!ble.idle()||!lightLayout.isChecked()||!car.lightingAvailable())return;byte[] identity=Arrays.copyOfRange(info,4,18);
        String label=s(enabled?R.string.car_light_on:R.string.car_light_off);
        new AlertDialog.Builder(this).setTitle(label).setMessage(s(R.string.car_light_confirm,label)).setNegativeButton(s(R.string.cancel),null).setPositiveButton(s(R.string.car_send),(dialog,which)->{if(carReady()&&ble.idle()&&lightLayout.isChecked()&&Arrays.equals(identity,Arrays.copyOfRange(info,4,18)))car.setBlinkHighBeam(enabled,true);}).show();
    }
    private void refreshCarUi(){
        if(carStatus==null)return;
        boolean busy=ota.active()||hardware.active()||captureStopping||car.active(),ready=carReady();
        lightLayout.setEnabled(!busy);
        for(Button b:carButtons)b.setEnabled(ready||(b==pressedSeat&&car.moving()));
        seatStop.setEnabled(car.moving());carVersionButton.setEnabled(ble.ready()&&!busy);
        carRefreshButton.setEnabled(canReadVehicle());
        lightOn.setEnabled(ready&&ble.idle()&&lightLayout.isChecked()&&car.lightingAvailable()&&!car.blinkHighBeam());
        lightOff.setEnabled(ready&&ble.idle()&&lightLayout.isChecked()&&car.lightingAvailable()&&car.blinkHighBeam());
        String line=!ble.ready()?s(R.string.disconnected):!car.telemetryFresh()?s(R.string.car_telemetry_unknown):s(R.string.car_telemetry,car.gear()==1?"P":car.gear()==2?"R":car.gear()==3?"N":car.gear()==4?"D":"?",car.speed());
        String code=carGateCode();String gateText=carGateText(code);if(!line.equals(gateText))line+="\n"+gateText;
        if(carTabVisible()&&!code.equals(lastCarGate)){lastCarGate=code;log("CAR GATE "+code+" statusBytes="+car.telemetryBytes()+" fresh="+car.telemetryFresh()+" gear="+car.gear()+" speed="+car.speed()+" directBodyControl=true");}
        putText(carReadiness,line);
    }
    private String carGateCode(){
        if(!ble.ready())return "BLE";if(leaving)return "BACKGROUND";if(ota.active())return "OTA";if(hardware.active()||captureStopping)return "CAPTURE";if(passwordRequired&&!passwordAccepted)return "AUTH";
        if(info==null)return "INFO";if((info[3]&1)==0)return "BOOT";return car.gate().name();
    }
    private String carGateText(String code){
        switch(code){
            case "BLE":return s(R.string.disconnected);case "BACKGROUND":return s(R.string.car_wait_foreground);case "OTA":return s(R.string.car_wait_ota);case "CAPTURE":return s(R.string.car_wait_capture);case "AUTH":return s(R.string.auth_required);
            case "PROFILE":return s(R.string.car_wait_profile);case "INFO":return s(R.string.car_wait_info);case "BOOT":return s(R.string.car_wait_normal);case "STATUS_MISSING":return s(R.string.car_wait_status);case "STATUS_SHORT":return s(R.string.car_short_status,car.telemetryBytes());case "STATUS_STALE":return s(R.string.car_stale_status);
            case "NOT_P":return s(R.string.car_wait_park,car.gear());case "SPEED":return s(R.string.car_wait_speed);case "READY":return s(R.string.car_control_ready);case "ACTIVE":return s(R.string.car_action_busy);default:return s(R.string.car_wait_transport);
        }
    }
    @Override protected void onSaveInstanceState(Bundle out){super.onSaveInstanceState(out);out.putInt("seat",selectedSeat);if(tabs!=null)out.putString("tab",tabs.getCurrentTabTag());}

    private void scan(){
        if(car.active())return;
        if(!permissions()){String[] p=Build.VERSION.SDK_INT>=31?new String[]{Manifest.permission.BLUETOOTH_SCAN,Manifest.permission.BLUETOOTH_CONNECT}:new String[]{Manifest.permission.ACCESS_FINE_LOCATION};requestPermissions(p,10);return;}
        BluetoothAdapter a=ble.adapter();if(a==null){state(s(R.string.no_bluetooth));return;}
        try{if(!a.isEnabled()){startActivity(new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE));return;}}
        catch(SecurityException e){state(s(R.string.permission_settings));return;}
        devices.clear();deviceList.removeAllViews();ble.scan();
    }
    private boolean permissions(){if(Build.VERSION.SDK_INT>=31)return checkSelfPermission(Manifest.permission.BLUETOOTH_SCAN)==PackageManager.PERMISSION_GRANTED&&checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT)==PackageManager.PERMISSION_GRANTED;return checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)==PackageManager.PERMISSION_GRANTED;}
    @Override public void onRequestPermissionsResult(int r,String[] p,int[] grants){super.onRequestPermissionsResult(r,p,grants);if(r==10){if(permissions())scan();else state(s(R.string.permission_denied));}}
    @Override public void found(BluetoothDevice d,String name,int rssi){
        String key=d.getAddress();if(devices.containsKey(key))return;devices.put(key,d);
        Button b=button(name+" · "+rssi+" dBm",()->{if(ota.active()||hardware.active()||captureStopping||car.active())return;selected=d;reconnects=0;clearIdentity();ble.connect(d);refresh();});deviceList.addView(b);
    }
    @Override public void state(String text){if(destroyed)return;status.setText(text);refresh();}
    private void clearIdentity(){closeVehicleAfterStop=false;car.transportLost();liveData.clear();versionInfo=null;if(lightLayout!=null)lightLayout.setChecked(false);displayVersions();info=null;passwordAccepted=false;passwordRequired=false;if(match!=null)match.setChecked(false);if(hw20!=null&&!ota.active())hw20.setChecked(false);deviceInfo.setText(s(R.string.info_not_ready));refresh();}
    @Override public void ready(){log("SESSION ready; request A0 device info");requestInfo();refresh();}
    private void requestInfo(){if(!ble.ready()||car.active()||(ota.active()&&!ota.waitingBoot()))return;lastCarInfoPoll=SystemClock.elapsedRealtime();ble.send(0xa0,new byte[0],()->log("A0 request sent"));}
    private void passwordDialog(){
        if(!ble.ready()||car.active()||(ota.active()&&!ota.waitingBoot()))return;EditText input=new EditText(this);input.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_PASSWORD);input.setHint(s(R.string.password_hint));input.setSaveEnabled(false);if(Build.VERSION.SDK_INT>=26)input.setImportantForAutofill(View.IMPORTANT_FOR_AUTOFILL_NO_EXCLUDE_DESCENDANTS);
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle(s(R.string.password_title)).setView(input).setNegativeButton(s(R.string.cancel),null).setPositiveButton(s(R.string.verify),null).create();
        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{String value=input.getText().toString();if(!value.matches("[\\x20-\\x7e]{4}")){input.setError(s(R.string.password_ascii));return;}byte[] b=value.getBytes(StandardCharsets.US_ASCII);input.setText("");passwordAccepted=false;log("AUTH manual attempt payload=redacted");ble.send(0xa8,b,()->Arrays.fill(b,(byte)0));dialog.dismiss();}));dialog.show();
    }
    @Override public void packet(Protocol.Packet packet){
        if(destroyed)return;
        if(packet.command==0xc0)liveData.onCan(packet.payload);
        boolean wasCapturing=hardware.active();int before=hardware.records();hardware.packet(packet.command,packet.payload);if(wasCapturing&&(before!=hardware.records()||!hardware.active()))hardwareChanged();
        if(wasCapturing&&!hardware.active())stopHardware(hardware.reason(),false);
        if(packet.command==0xb0){liveData.onStatus(packet.payload);car.onTelemetry(packet.payload);log("CAR STATUS B0 len="+packet.payload.length+" fieldsValid="+(packet.payload.length>=4)+" gear="+car.gear()+" speed="+car.speed()+" payload=redacted");car.tick();refresh();return;}
        if(packet.command==0xa3){log("CAR A3 echo received; A0 required for readback confirmation");return;}
        if(packet.command==0xa8&&packet.payload.length>0){int result=packet.payload[0]&255;
            if(result==1){passwordAccepted=true;log("AUTH accepted");if(!ota.active()||ota.waitingBoot())requestInfo();}
            else{passwordAccepted=false;passwordRequired=true;car.setAvailable(false);car.cancel();if(hardware.active())stopHardware("auth_required",false);log(result==255?"AUTH password required":"AUTH rejected; no automatic retries");if(ota.active()&&!ota.waitingBoot())ota.fail(s(R.string.auth_changed));state(result==255?s(R.string.auth_required):s(R.string.auth_rejected));}refresh();return;
        }
        if(packet.command==0xa0){
            if(packet.payload.length<18){info=null;versionInfo=null;car.onInfo(packet.payload);match.setChecked(false);if(lightLayout!=null)lightLayout.setChecked(false);displayVersions();deviceInfo.setText(s(R.string.info_not_ready));state(s(R.string.info_short));log("A0 invalid len="+packet.payload.length+"; control authorization revoked");refresh();return;}
            int oldIdentityEpoch=car.identityEpoch();info=packet.payload.clone();versionInfo=DeviceInfoSnapshot.parse(info,SystemClock.elapsedRealtime());car.onInfo(info);if(oldIdentityEpoch!=car.identityEpoch()&&lightLayout!=null)lightLayout.setChecked(false);displayVersions();deviceInfo.setText(s(R.string.device_info,info[0]&255,info[2]&255,(info[3]&1)==0?s(R.string.boot_mode):s(R.string.run_mode)));
            log("A0 validated len="+info.length+" hwByte="+(info[0]&255)+" btVersionByte="+(info[1]&255)+" appVersionByte="+(info[2]&255)+" normalMode="+((info[3]&1)!=0));if(!passwordRequired||passwordAccepted)ota.onDeviceInfo(info);refresh();return;
        }ota.onPacket(packet.command,packet.payload);
    }
    @Override public void disconnected(){
        captureStopping=false;disconnectAfterCaptureStop=false;canStreaming=false;if(destroyed)return;
        if(hardware.active())stopHardware("disconnected",false);
        clearIdentity();ota.transportLost();
        if(ota.waitingBoot()&&!leaving&&selected!=null&&reconnects<3){int attempt=++reconnects;log("BOOT reconnect attempt="+attempt+"/3 same selected device");handler.postDelayed(()->{if(!destroyed&&!leaving&&ota.waitingBoot()&&selected!=null)ble.connect(selected);},1500);}
        refresh();
    }
    private void parseSelected(){
        match.setChecked(false);image=null;
        try{image=FirmwareImage.parse(selectedBytes,FirmwareImage.Format.values()[format.getSelectedItemPosition()]);fileInfo.setText(s(R.string.file_details,imageName,image.fileBytes,image.pageCount(),image.paddingBytes,image.sha256,image.transferSha256));log("BIN validated format="+image.format+" bytes="+image.fileBytes+" pages="+image.pageCount()+" padding="+image.paddingBytes+" sha256="+image.sha256+" transferSha256="+image.transferSha256);}
        catch(IllegalArgumentException e){fileInfo.setText(imageName+"\n"+UiStrings.error(this,e));log("BIN rejected: "+e.getMessage());}refresh();
    }
    private void confirmFlash(){
        if(!canFlash())return;FirmwareImage confirmed=image;byte[] identity=Arrays.copyOfRange(info,4,18);boolean confirmedHw20=hw20.isChecked();
        new AlertDialog.Builder(this).setTitle(s(R.string.flash_title)).setMessage(s(R.string.flash_confirm,image.pageCount(),image.paddingBytes,confirmedHw20?s(R.string.policy_hw20):s(R.string.policy_reply),image.sha256,image.transferSha256))
            .setNegativeButton(s(R.string.cancel),null).setPositiveButton(s(R.string.flash_start),(dialog,which)->{if(canFlash()&&confirmed==image&&confirmedHw20==hw20.isChecked()&&Arrays.equals(identity,Arrays.copyOfRange(info,4,18))){ota.start(image,identity,confirmedHw20);refresh();}}).show();
    }
    private boolean canFlash(){return ble!=null&&ble.ready()&&info!=null&&image!=null&&match.isChecked()&&!ota.active()&&!car.active()&&!hardware.active()&&!captureStopping&&uidValid()&&(!passwordRequired||passwordAccepted);}
    private boolean uidValid(){if(info==null||info.length<18)return false;for(int j=4;j<18;j++)if(info[j]!=0)return true;return false;}
    @Override public void send(int command,byte[] data,Runnable done){ble.send(command,data,done);}
    @Override public void changed(UiMessage detail){if(destroyed)return;stage.setText(message(detail));log("STATE "+ota.state()+" "+detail);if(ota.failed()){ble.close();clearIdentity();}refresh();}
    private boolean canChangeLanguage(){return ble!=null&&!ble.open()&&!car.active()&&!ota.active()&&!hardware.active()&&!captureStopping;}
    private String captureReason(){
        switch(hardware.reason()){
            case "manual": return s(R.string.reason_manual);
            case "user_disconnect":case "disconnected": return s(R.string.reason_disconnected);
            case "background":case "activity_destroyed": return s(R.string.reason_background);
            case "auth_required": return s(R.string.reason_auth_required);
            case "duration_limit": return s(R.string.reason_time_limit);
            case "record_limit": return s(R.string.reason_record_limit);
            case "size_limit": return s(R.string.reason_byte_limit);
            case "recording": return s(R.string.reason_running);
            default:return s(R.string.reason_other);
        }
    }
    private static String localeSignature(android.content.res.Configuration config){
        return (Build.VERSION.SDK_INT>=24?config.getLocales().toLanguageTags():config.locale.toLanguageTag())+"/"+config.getLayoutDirection();
    }
    @Override public void onConfigurationChanged(android.content.res.Configuration config){
        super.onConfigurationChanged(config);
        // Framework app-language and system-language changes must not stop a live BLE operation.
        pendingLanguageRefresh=!localeSignature(config).equals(displayedLocale);refresh();
    }
    private void refresh(){
        if(flashButton==null||destroyed)return;boolean active=ota.active(),ready=ble.ready();
        boolean recording=hardware.active()||captureStopping,carActive=car.active();
        car.setAvailable(ready&&!leaving&&!active&&!recording&&info!=null&&(info[3]&1)!=0&&(!passwordRequired||passwordAccepted));
        language.setEnabled(canChangeLanguage());languageButton.setEnabled(canChangeLanguage());putText(headerConnection,s(ready?R.string.ui_connected:R.string.disconnected));headerConnection.setTextColor(ready?GREEN:MUTED);if(recording)captureDetails.setVisibility(View.VISIBLE);
        scanButton.setEnabled(!active&&!carActive&&!ready&&!recording);disconnectButton.setEnabled(ready||active||recording);readButton.setEnabled(ready&&!active&&!recording&&!carActive);passwordButton.setEnabled(ready&&!recording&&!carActive&&(!active||ota.waitingBoot()));versionButton.setEnabled(ready&&!active&&!recording&&!carActive);
        fileButton.setEnabled(!active&&!recording&&!carActive);format.setEnabled(!active&&!recording&&!carActive);match.setEnabled(!active&&!recording&&!carActive);hw20.setEnabled(!active&&!recording&&!carActive);exportButton.setEnabled(!active&&!recording&&!carActive);flashButton.setEnabled(canFlash());cancelButton.setEnabled(active);
        captureStart.setEnabled(ready&&!active&&!carActive&&!recording&&(!passwordRequired||passwordAccepted));captureStop.setEnabled(hardware.active());captureMode.setEnabled(!active&&!recording&&!carActive);canIds.setEnabled(!active&&!recording&&!carActive);canData.setEnabled(!active&&!recording&&!carActive);hardwareExport.setEnabled(!active&&!recording&&!carActive&&(hardwareSession||!previousHardware.isEmpty()));
        refreshCarUi();
        if(livePanel!=null)livePanel.update(liveData,ready,telemetryTabVisible()&&canReadVehicle(),canStartLiveCan(),hardware.active()&&hardware.mode()==HardwareCapture.Mode.CAN,hardwareExport.isEnabled(),recording);
        progress.setProgress(ota.success()?100:ota.total()>0?Math.min(99,ota.page()*100/ota.total()):0);
        if(active||recording||carActive)getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);else getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        if(pendingLanguageRefresh&&!leaving&&!isFinishing()&&canChangeLanguage()){
            pendingLanguageRefresh=false;handler.post(()->{if(!destroyed&&!leaving&&!isFinishing()&&canChangeLanguage())recreate();else pendingLanguageRefresh=true;});return;
        }
    }
    @Override public void log(String line){
        if(destroyed)return;String stamp=new SimpleDateFormat("HH:mm:ss.SSS",Locale.ROOT).format(new Date());String safe=line.replace('\n',' ').replace('\r',' ');logs.append(stamp).append(' ').append(safe).append('\n');
        if(logs.length()>200000)logs.delete(0,logs.length()-160000);logDirty=true;android.util.Log.d("Tsl9Updater",safe);
        if(!logScheduled){logScheduled=true;handler.postDelayed(()->{logScheduled=false;if(destroyed)return;String all=logs.toString();if(logView!=null)logView.setText(all.substring(Math.max(0,all.length()-12000)));flushLog();},300);}
    }
    private void flushLog(){if(!logDirty||logFile==null)return;try(FileOutputStream out=new FileOutputStream(logFile)){out.write(logs.toString().getBytes(StandardCharsets.UTF_8));logDirty=false;}catch(IOException ignored){}}
    private final Runnable ticker=new Runnable(){public void run(){if(destroyed)return;boolean capturing=hardware.active();hardware.tick();if(capturing&&!hardware.active())stopHardware(hardware.reason(),false);ota.tick();car.tick();refresh();pollCar();long now=SystemClock.elapsedRealtime();if(ota.waitingBoot()&&ble.idle()&&now-lastBootPoll>=1000&&(!passwordRequired||passwordAccepted)){lastBootPoll=now;requestInfo();}handler.postDelayed(this,200);}};
    private static byte[] readLimited(InputStream stream,int max)throws IOException{if(stream==null)throw new IOException("File provider returned no stream");try(InputStream in=stream;ByteArrayOutputStream out=new ByteArrayOutputStream()){byte[] buf=new byte[8192];int n;while((n=in.read(buf))!=-1){if(out.size()+n>max)throw new IOException("File exceeds size limit");out.write(buf,0,n);}return out.toByteArray();}}
    @Override protected void onActivityResult(int request,int result,Intent data){
        super.onActivityResult(request,result,data);if(result!=RESULT_OK||data==null||data.getData()==null)return;
        if(request==100){try{selectedBytes=readLimited(getContentResolver().openInputStream(data.getData()),FirmwareImage.MAX_PAGES*FirmwareImage.PAGE);imageName="selected.bin";try(Cursor c=getContentResolver().query(data.getData(),new String[]{OpenableColumns.DISPLAY_NAME},null,null,null)){if(c!=null&&c.moveToFirst())imageName=c.getString(0);}parseSelected();}catch(IOException|SecurityException e){selectedBytes=null;image=null;fileInfo.setText(s(R.string.file_read_error,e.getClass().getSimpleName()));log("BIN read failed "+e.getClass().getSimpleName());refresh();}}
        if(request==101){try(OutputStream out=getContentResolver().openOutputStream(data.getData(),"wt")){if(out==null)throw new IOException();out.write(logs.toString().getBytes(StandardCharsets.UTF_8));state(s(R.string.debug_exported));}catch(IOException|SecurityException e){state(s(R.string.debug_export_failed));}}
        if(request==102){try(OutputStream out=getContentResolver().openOutputStream(data.getData(),"wt")){if(out==null)throw new IOException();out.write(hardwareSnapshot().getBytes(StandardCharsets.UTF_8));state(s(R.string.hardware_exported));}catch(IOException|SecurityException e){state(s(R.string.hardware_export_failed));}}
    }
    @Override protected void onResume(){super.onResume();leaving=false;refresh();}
    @Override protected void onStop(){super.onStop();leaving=true;if(car.active()){closeVehicleAfterStop=true;car.cancel();}if(hardware.active()||canStreaming||captureStopping)stopHardware("background",true);if(ota.active()){ota.cancel(s(R.string.reason_background));ble.close();clearIdentity();}flushHardware();flushLog();}
    @Override protected void onDestroy(){ota.cancel(s(R.string.destroyed));if(car.active()){closeVehicleAfterStop=true;car.cancel();}if(!car.active())stopHardware("activity_destroyed",true);flushHardware();flushLog();destroyed=true;handler.removeCallbacksAndMessages(null);if(captureStopping||car.active())handler.postDelayed(()->{ble.close();captureStopping=false;disconnectAfterCaptureStop=false;},8000);super.onDestroy();}

    private boolean canStartLiveCan(){return !leaving&&ble.idle()&&!ota.active()&&!car.active()&&!hardware.active()&&!captureStopping&&info!=null&&(info[3]&1)!=0&&(!passwordRequired||passwordAccepted);}
    private void startLiveCan(String filter){
        if(!canStartLiveCan())return;HardwareCapture.canFilter(filter);canIds.setText(filter);captureMode.setSelection(HardwareCapture.Mode.CAN.ordinal());startHardware();
    }
    private void startHardware(){
        if(!ble.ready()||ota.active()||car.active()||hardware.active()||captureStopping||(passwordRequired&&!passwordAccepted))return;
        HardwareCapture.Mode mode=HardwareCapture.Mode.values()[captureMode.getSelectedItemPosition()];
        byte[] request=mode==HardwareCapture.Mode.CAN?HardwareCapture.canFilter(canIds.getText().toString()):null;
        if(mode==HardwareCapture.Mode.CAN&&(info==null||(info[3]&1)==0)){state(s(R.string.can_requires_app));return;}
        if(mode==HardwareCapture.Mode.CAN)liveData.clearCan();hardware.start(mode,canData.isChecked());hardwareSession=true;hardwareChanged();log("HARDWARE capture start mode="+mode+" dataOptIn="+canData.isChecked());
        if(mode==HardwareCapture.Mode.CAN){canStreaming=true;ble.send(0xc0,request,()->log("CAN subscription request sent; hardware replies not yet confirmed"));}
        else if(mode==HardwareCapture.Mode.BLE)requestInfo();
        refresh();
    }
    private void stopHardware(String reason,boolean disconnectAfter){
        hardware.stop(reason);if(hardwareSession)hardwareChanged();
        disconnectAfterCaptureStop|=disconnectAfter;
        if(captureStopping){flushHardware();refresh();return;}
        boolean sendStop=canStreaming&&ble.ready();canStreaming=false;
        if(sendStop){captureStopping=true;log("CAN stop requested");ble.send(0xc0,new byte[]{0},()->{log("CAN stop frame sent; peripheral stop not acknowledged");finishHardwareStop();});}
        else finishHardwareStop();
        flushHardware();refresh();
    }
    private void finishHardwareStop(){captureStopping=false;boolean close=disconnectAfterCaptureStop||destroyed;disconnectAfterCaptureStop=false;if(close){ble.close();if(!destroyed)clearIdentity();}if(!destroyed)refresh();}
    @Override public void notification(byte[] bytes){if(destroyed)return;boolean before=hardware.active();int n=hardware.records();hardware.notification(bytes);if(before&&(n!=hardware.records()||!hardware.active()))hardwareChanged();if(before&&!hardware.active())stopHardware(hardware.reason(),false);}
    private void hardwareChanged(){
        hardwareDirty=true;hardwareStatus.setText(s(R.string.capture_summary,s(hardware.active()?R.string.recording:R.string.capture_stopped),hardware.records(),captureReason(),hardware.records()==0?s(R.string.no_hardware_data):""));
        if(!hardwareScheduled){hardwareScheduled=true;handler.postDelayed(()->{hardwareScheduled=false;if(destroyed)return;hardwareView.setText(hardware.preview());flushHardware();},1000);}refresh();
    }
    private String hardwareSnapshot(){return hardwareSession?hardware.snapshot():previousHardware;}
    private void flushHardware(){if(!hardwareDirty||!hardwareSession)return;android.util.AtomicFile file=new android.util.AtomicFile(hardwareFile);FileOutputStream out=null;try{out=file.startWrite();out.write(hardware.snapshot().getBytes(StandardCharsets.UTF_8));file.finishWrite(out);hardwareDirty=false;}catch(IOException e){if(out!=null)file.failWrite(out);hardwareStatus.setText(s(R.string.hardware_save_failed));}}
}
