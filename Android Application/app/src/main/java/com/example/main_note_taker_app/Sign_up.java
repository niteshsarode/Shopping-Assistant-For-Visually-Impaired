package com.example.main_note_taker_app;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.Window;
import android.widget.Button;
import android.widget.EditText;

import org.w3c.dom.Text;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.util.HashMap;
import java.util.Map;

import static androidx.constraintlayout.widget.Constraints.TAG;

public class Sign_up extends AppCompatActivity {
    private Button sign_up;
    private EditText usernameText;
    private EditText passwordText;
    private EditText emailText;

    private String username;
    private String password;
    private String email;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_sign_up);
        getWindow().setFeatureInt(Window.FEATURE_CUSTOM_TITLE, R.id.myTitle);
        sign_up = (Button) findViewById(R.id.Sign_up);
        sign_up.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                add_user();
            }
        });
        usernameText = (EditText)findViewById(R.id.fname);
        passwordText = (EditText)findViewById(R.id.password);
        emailText = (EditText)findViewById(R.id.email);

    }

    public void add_user(){

        username = usernameText.getText().toString();
        email = emailText.getText().toString();
        password = passwordText.getText().toString();

        AsyncTaskRunner runner = new AsyncTaskRunner();

        runner.execute();

    }

    private class AsyncTaskRunner extends AsyncTask<String, String, String> {

        private String response;
        //ProgressDialog progressDialog;

        @Override
        protected String doInBackground(String... params) {
            publishProgress("Sleeping..."); // Calls onProgressUpdate()

            try {
                String response = "";
                URL url = new URL("https://shoppingassitant-275209.uc.r.appspot.com/add_user");
//                URL url = new URL("http://192.168.0.18:8080/add_user");
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setRequestProperty("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");


                HashMap<String, String> attr = new HashMap<>();


                attr.put("user_name", username);
                attr.put("password", password);
                attr.put("email", email);


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
                        if(line.equals("added"))
                            return "done";
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
}
