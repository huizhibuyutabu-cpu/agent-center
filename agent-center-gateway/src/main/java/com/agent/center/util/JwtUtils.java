package com.agent.center.util;

import cn.hutool.crypto.asymmetric.RSA;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.Jwts;
import lombok.extern.slf4j.Slf4j;

import java.util.Map;

/**
 * jwt工具类，提供生成token与校验token的方法，采用RSA非对称加密
 */
@Slf4j
public class JwtUtils {

    /**
     * 校验token
     *
     * @param token        token字符串
     * @param publicKeyStr RSA公钥字符串
     * @return token解密数据
     */
    public static Map<String, Object> checkToken(String token, String publicKeyStr) {
        RSA rsa = new RSA(null, publicKeyStr);
        try {
            // 通过token解析数据
            return Jwts.parser()
                    .setSigningKey(rsa.getPublicKey()) //设置校验token签名的密钥
                    .parseClaimsJws(token)
                    .getBody();
        } catch (ExpiredJwtException e) {
            // token已经过期！
        } catch (Exception e) {
            log.error("token非法传入，token = {}", token, e);
        }

        return null;
    }

}
