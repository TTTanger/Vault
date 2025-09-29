#!/usr/bin/swift

import Foundation
import LocalAuthentication

let context = LAContext()
var error: NSError?

// 检查生物识别是否可用
if context.canEvaluatePolicy(.biometryAny, error: &error) {
    let reason = "验证身份以访问密码保险库"
    
    context.evaluatePolicy(.biometryAny, localizedReason: reason) { success, authenticationError in
        DispatchQueue.main.async {
            if success {
                print("TOUCHID_SUCCESS")
            } else {
                if let error = authenticationError as? LAError {
                    switch error.code {
                    case .userCancel:
                        print("TOUCHID_CANCELLED")
                    case .userFallback:
                        print("TOUCHID_FALLBACK")
                    case .biometryNotAvailable:
                        print("TOUCHID_NOT_AVAILABLE")
                    case .biometryNotEnrolled:
                        print("TOUCHID_NOT_ENROLLED")
                    case .biometryLockout:
                        print("TOUCHID_LOCKOUT")
                    default:
                        print("TOUCHID_ERROR")
                    }
                } else {
                    print("TOUCHID_ERROR")
                }
            }
            exit(0)
        }
    }
    
    // 保持程序运行直到回调完成
    RunLoop.main.run()
} else {
    if let error = error {
        print("TOUCHID_NOT_AVAILABLE: \(error.localizedDescription)")
    } else {
        print("TOUCHID_NOT_AVAILABLE")
    }
}

