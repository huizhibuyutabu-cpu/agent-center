package com.agent.center.filter;

import cn.hutool.core.map.MapUtil;
import cn.hutool.core.util.ObjectUtil;
import cn.hutool.core.util.StrUtil;
import com.agent.center.util.JwtUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

@Component
public class AuthFilter implements GlobalFilter, Ordered {

    @Value("${jwt.public-key}")
    private String publicKey;

    public static final String AUTHORIZATION_HEADER = "Authorization";

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        var path = exchange.getRequest().getPath().toString();
        if (StrUtil.startWithAny(path, "/auth/token")) {
            //直接放行
            return chain.filter(exchange);
        }

        var token = exchange.getRequest().getHeaders().getFirst(AUTHORIZATION_HEADER);
        if (ObjectUtil.isEmpty(token)) {
            //设置响应状态为401
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            //拦截请求
            return exchange.getResponse().setComplete();
        }

        // 校验token
        var bodyData = JwtUtils.checkToken(token, this.publicKey);
        if (ObjectUtil.isEmpty(bodyData)) {
            //设置响应状态为401
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            //拦截请求
            return exchange.getResponse().setComplete();
        }

        // token有效，向下游传递用户信息
        exchange.mutate()
                .request(builder -> builder
                        .header("app_id", MapUtil.get(bodyData, "app_id", String.class))
                        .header("app_key", MapUtil.get(bodyData, "app_key", String.class))
                        .header("token", token)
                        .header("request-from", "agent-center-gateway")
                )
                .build();

        // 放行请求
        return chain.filter(exchange);
    }

    @Override
    public int getOrder() {
        return Ordered.LOWEST_PRECEDENCE;
    }
}