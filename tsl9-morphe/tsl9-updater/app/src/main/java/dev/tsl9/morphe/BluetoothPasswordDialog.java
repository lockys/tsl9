package dev.tsl9.morphe;

import android.app.AlertDialog;
import android.content.Context;
import android.os.Build;
import android.text.InputType;
import android.view.View;
import android.widget.EditText;
import java.nio.charset.StandardCharsets;

/** Password UI with an explicit submit action; opening it never authenticates. */
final class BluetoothPasswordDialog {
    interface Events {void submit(byte[] password);void rememberFailed();}
    static AlertDialog create(Context context,BluetoothPasswordStore store,Events events){
        EditText input=new EditText(context);input.setId(android.R.id.edit);
        input.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_PASSWORD);
        input.setHint(context.getString(R.string.password_hint));input.setSaveEnabled(false);
        if(Build.VERSION.SDK_INT>=26)input.setImportantForAutofill(View.IMPORTANT_FOR_AUTOFILL_NO_EXCLUDE_DESCENDANTS);
        input.setText(store.load());input.selectAll();
        AlertDialog dialog=new AlertDialog.Builder(context).setTitle(context.getString(R.string.password_title)).setView(input).setNegativeButton(context.getString(R.string.cancel),null).setPositiveButton(context.getString(R.string.verify),null).create();
        dialog.setOnDismissListener(ignored->input.setText(""));
        dialog.setOnShowListener(ignored->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(view->{
            String value=input.getText().toString();
            if(!BluetoothPasswordStore.valid(value)){input.setError(context.getString(R.string.password_ascii));return;}
            if(!store.remember(value))events.rememberFailed();
            byte[] payload=value.getBytes(StandardCharsets.US_ASCII);input.setText("");
            events.submit(payload);dialog.dismiss();
        }));
        return dialog;
    }
}
