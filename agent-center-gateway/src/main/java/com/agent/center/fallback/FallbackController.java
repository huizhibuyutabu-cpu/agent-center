package com.agent.center.fallback;

import cn.hutool.json.JSONUtil;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

import java.util.Map;

@RestController
public class FallbackController {

    @RequestMapping("/fallback/ac")
    public Mono<String> courseFallback() {
        var message = Map.of(
                "status", "500",
                "message", "AgentCenter service is unavailable now, please try later.");
        return Mono.just(JSONUtil.toJsonStr(message));
    }
}