package com.example.heatingmonitor.controller; 
 
import org.springframework.web.bind.annotation.GetMapping; 
import org.springframework.web.bind.annotation.RestController; 
import java.util.HashMap; 
import java.util.Map; 
 
@RestController 
public class StatusController { 
 
    @GetMapping("/api/status") 
    public Map<String, String> getStatus() { 
        Map<String, String> status = new HashMap<>(); 
        status.put("status", "OK"); 
        status.put("message", "Heating Monitor Backend is running"); 
        status.put("version", "v2.0-dev"); 
        return status; 
    } 
} 
