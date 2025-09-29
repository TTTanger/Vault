#import <Foundation/Foundation.h>
#import <LocalAuthentication/LocalAuthentication.h>

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        LAContext *context = [[LAContext alloc] init];
        NSError *error = nil;
        
        // 检查生物识别是否可用
        if ([context canEvaluatePolicy:LAPolicyDeviceOwnerAuthenticationWithBiometrics error:&error]) {
            // 只有一个参数时才进行认证，否则只检查可用性
            if (argc > 1 && strcmp(argv[1], "--auth") == 0) {
                NSString *reason = @"验证身份以访问密码保险库";
                
                [context evaluatePolicy:LAPolicyDeviceOwnerAuthenticationWithBiometrics
                        localizedReason:reason
                                  reply:^(BOOL success, NSError * _Nullable error) {
                    if (success) {
                        printf("TOUCHID_SUCCESS\n");
                    } else {
                        if (error) {
                            switch (error.code) {
                                case LAErrorUserCancel:
                                    printf("TOUCHID_CANCELLED\n");
                                    break;
                                case LAErrorUserFallback:
                                    printf("TOUCHID_FALLBACK\n");
                                    break;
                                case LAErrorBiometryNotAvailable:
                                    printf("TOUCHID_NOT_AVAILABLE\n");
                                    break;
                                case LAErrorBiometryNotEnrolled:
                                    printf("TOUCHID_NOT_ENROLLED\n");
                                    break;
                                case LAErrorBiometryLockout:
                                    printf("TOUCHID_LOCKOUT\n");
                                    break;
                                default:
                                    printf("TOUCHID_ERROR: %s\n", [error.localizedDescription UTF8String]);
                                    break;
                            }
                        } else {
                            printf("TOUCHID_ERROR\n");
                        }
                    }
                    exit(0);
                }];
                
                // 保持程序运行直到回调完成
                [[NSRunLoop mainRunLoop] run];
            } else {
                // 只检查可用性，不进行认证
                printf("TOUCHID_AVAILABLE\n");
            }
            
        } else {
            if (error) {
                printf("TOUCHID_NOT_AVAILABLE: %s\n", [error.localizedDescription UTF8String]);
            } else {
                printf("TOUCHID_NOT_AVAILABLE\n");
            }
        }
    }
    return 0;
}
