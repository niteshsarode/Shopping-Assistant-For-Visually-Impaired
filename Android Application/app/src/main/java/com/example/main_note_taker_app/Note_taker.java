package com.example.main_note_taker_app;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.speech.RecognizerIntent;
import android.util.Log;
import android.view.View;
import android.view.Window;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;
import android.widget.Toast;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import static androidx.constraintlayout.widget.Constraints.TAG;

public class Note_taker extends AppCompatActivity {

    private static final int REQUEST_CODE = 100;
    ArrayList<String> final_res = new ArrayList<String>();
    ListView listView;
    ArrayAdapter<String> adapter;
    int clickCounter=0;
    int user_id = 0;
    DatabaseReference reference;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_note_taker);
//        getWindow().setFeatureInt(Window.FEATURE_CUSTOM_TITLE, R.id.myTitle);

        Intent intent = getIntent();
        user_id = intent.getIntExtra("user_id", 0);

        Button Record = (Button) findViewById(R.id.startDictation);
        Button Done = (Button) findViewById(R.id.Done);
        Button Camera = (Button) findViewById(R.id.Record);
        Camera.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                openCamera();
            }
        });

        reference = FirebaseDatabase.getInstance().getReference().child("List");

        listView = (ListView) findViewById(R.id.simpleListView);
        adapter = new ArrayAdapter<String>(this, android.R.layout.simple_list_item_1, final_res);
        listView.setAdapter(adapter);

        Record.setOnClickListener(new View.OnClickListener(){
            public void onClick(View v)
            {

                //Trigger the RecognizerIntent intent//

                Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);

                try {
                    startActivityForResult(intent, REQUEST_CODE);
                } catch (ActivityNotFoundException a) {

                }
            }
        });

        Done.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v)
            {

                reference.setValue(final_res).addOnCompleteListener(new OnCompleteListener<Void>() {
                    @Override
                    public void onComplete(@NonNull Task<Void> task) {
                        if(task.isSuccessful()){
                            Toast.makeText(getApplicationContext(),"List is uploaded successfully", Toast.LENGTH_LONG).show();
                        }
                    }
                });

                AsyncTaskRunner runner = new AsyncTaskRunner();

                runner.execute();
            }
        });

    }

    private class AsyncTaskRunner extends AsyncTask<String, String, String> {

        private String response;
        //ProgressDialog progressDialog;

        @Override
        protected String doInBackground(String... params) {
            publishProgress("Sleeping..."); // Calls onProgressUpdate()

            try {
                String response = "";

                URL url = new URL("https://shoppingassitant-275209.uc.r.appspot.com/add_user_list");
//                URL url = new URL("http://192.168.0.18:8080/add_user_list");
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setRequestProperty("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");


                HashMap<String, String> attr = new HashMap<>();

                String user_list_str = "";

                for (String s : final_res)
                {
                    user_list_str += s + ",";
                }

                attr.put("user_list", user_list_str);
                attr.put("user_id", String.valueOf(user_id));


                String paramsString = getPostDataString(attr);

                DataOutputStream wr = new DataOutputStream(conn.getOutputStream());
                wr.writeBytes(paramsString);
                wr.flush();
                wr.close();


                int responseCode = conn.getResponseCode();

                Log.e(TAG, "13 - responseCode : " + responseCode);

                if (responseCode == HttpURLConnection.HTTP_OK) {
                    Log.e(TAG, "14 - HTTP_OK");

                    String line;
                    BufferedReader br = new BufferedReader(new InputStreamReader(
                            conn.getInputStream()));
                    while ((line = br.readLine()) != null) {
                        response += line;
                        Log.d("ResponseLine", response);
                    }
                } else {
                    Log.e(TAG, "14 - False - HTTP_OK");
                    response = "";
                }
            } catch(Exception e) {
                e.printStackTrace();
            }
            return "can not add";
        }

        private String getPostDataString(HashMap<String, String> params) throws UnsupportedEncodingException {
            StringBuilder result = new StringBuilder();
            boolean first = true;
            for(Map.Entry<String, String> entry : params.entrySet()){
                if (first)
                    first = false;
                else
                    result.append("&");

                result.append(URLEncoder.encode(entry.getKey(), "UTF-8"));
                result.append("=");
                result.append(URLEncoder.encode(entry.getValue(), "UTF-8"));
            }

            return result.toString();
        }


        @Override
        protected void onPostExecute(String result) {
            if(result.equals("done")) {
                Intent intent = new Intent(getApplicationContext(), MainActivity.class);
                startActivity(intent);
            } else {
                Intent intent = new Intent(getApplicationContext(), Sign_up.class);
                startActivity(intent);
            }
        }


        @Override
        protected void onPreExecute() {

        }


        @Override
        protected void onProgressUpdate(String... text) {

        }
    }

    public void openCamera(){
        Intent intent = new Intent(this, CameraOpen.class);
        intent.putExtra("user_id", user_id);
        startActivity(intent);
    }

    @Override
    //Handle the results//
    //Define an OnActivityResult method in our intent caller Activity//

    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        switch (requestCode) {
            case REQUEST_CODE: {

                //If RESULT_OK is returned...//

                if (resultCode == RESULT_OK && null != data) {

                    //...then retrieve the ArrayList//

                    ArrayList<String> result = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);

                    final_res.add(result.get(0));
                    clickCounter++;
                    adapter.notifyDataSetChanged();

                }
                break;
            }

        }
        for(int i=0; i<final_res.size();i++){
            Log.d("List",final_res.get(i));
        }


    }
}
