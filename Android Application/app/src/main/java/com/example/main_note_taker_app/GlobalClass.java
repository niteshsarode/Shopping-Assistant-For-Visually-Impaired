package com.example.main_note_taker_app;

import android.app.Application;

public class GlobalClass extends Application {

    private String name;
    private String email;
    private int user_id;


    public String getName() {

        return name;
    }

    public void setName(String aName) {

        name = aName;

    }

    public String getEmail() {

        return email;
    }

    public void setEmail(String aEmail) {

        email = aEmail;
    }

    public int getUserId() {

        return user_id;
    }

    public void setUserId(int aUserId) {

        user_id = aUserId;
    }
}

