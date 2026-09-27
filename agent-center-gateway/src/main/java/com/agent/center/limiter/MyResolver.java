package com.agent.center.limiter;

import org.springframework.cloud.gateway.filter.ratelimit.KeyResolver;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import reactor.core.publisher.Mono;

@Configuration
public class MyResolver {

    @Bean
    public KeyResolver apiKeyResolver() {
        return exchange -> Mono.just(exchange.getRequest().getPath().value());
    }

}