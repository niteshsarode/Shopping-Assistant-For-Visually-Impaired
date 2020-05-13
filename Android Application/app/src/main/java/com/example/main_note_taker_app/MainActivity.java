package com.example.main_note_taker_app;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.Window;
import android.widget.Button;
import android.widget.EditText;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.ByteBuffer;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static androidx.constraintlayout.widget.Constraints.TAG;

public class MainActivity extends AppCompatActivity {
    private Button Login;
    private Button Sign_up;

    private EditText usernameText;
    private EditText passwordText;


    private String username;
    private String password;

    private int user_id;
    GlobalClass globalVariable;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        getWindow().setFeatureInt(Window.FEATURE_CUSTOM_TITLE, R.id.myTitle);
        Sign_up = (Button) findViewById(R.id.Sign_up);
        Login = (Button) findViewById(R.id.Login);
        passwordText = (EditText)findViewById(R.id.password_login);
        usernameText = (EditText)findViewById(R.id.username_login);

        globalVariable = (GlobalClass) getApplicationContext();

        Login.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                get_user();
            }
        });

        Sign_up.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                openSignUp();
            }
        });


    }

    public void get_user(){

        username = usernameText.getText().toString();
        password = passwordText.getText().toString();

        AsyncTaskRunner runner = new AsyncTaskRunner();

        runner.execute();

    }

    public void openSignUp(){
        Intent intent = new Intent(this, Sign_up.class);
        startActivity(intent);
    }

    private class AsyncTaskRunner extends AsyncTask<String, String, String> {

        private String response;
        //ProgressDialog progressDialog;

        @Override
        protected String doInBackground(String... params) {
            publishProgress("Sleeping..."); // Calls onProgressUpdate()

            try {
                String response = "";
                URL url = new URL("https://shoppingassitant-275209.uc.r.appspot.com/get_user");
//                URL url = new URL("http://192.168.0.18:8080/get_user");
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setRequestProperty("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");


                HashMap<String, String> attr = new HashMap<>();

                attr.put("user_name", username);
                attr.put("password", password);


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
                        String[] keywords = line.split(" ");
                        if(keywords[0].equals("Found")) {
                            user_id = Integer.parseInt(keywords[1]);
                            return "found";
                        }
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
            return "not found";
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
            if(result.equals("found")) {
                Intent intent = new Intent(getApplicationContext(), Note_taker.class);
                intent.putExtra("user_id", user_id);
                globalVariable.setUserId(user_id);
                startActivity(intent);
            } else {
                Intent intent = new Intent(getApplicationContext(), MainActivity.class);
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
