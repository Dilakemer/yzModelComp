from database import SessionLocal, init_db
from models import ErrorCategory, ErrorType

# Tablodaki hata kategorileri ve tipleri
ERROR_DATA = {
    "API_ERR": {
        "name": "API Hataları",
        "types": [
            "400 Bad Request",
            "401 Unauthorized", 
            "403 Forbidden",
            "404 Not Found",
            "500 Internal Server Error",
            "502 Bad Gateway",
            "503 Service Unavailable",
            "504 Gateway Timeout"
        ]
    },
    "AUTO_ERR": {
        "name": "Otomasyon Hataları",
        "types": [
            "NoSuchElementException",
            "TimeoutException",
            "StaleElementReferenceException",
            "ElementNotInteractableException",
            "ElementClickInterceptedException",
            "InvalidSelectorException"
        ]
    },
    "BROWSER_ERR": {
        "name": "Tarayıcı Hataları",
        "types": [
            "BrowserNotReachableException",
            "BrowserCrashDetected",
            "TabCrashException",
            "WebDriverException",
            "SessionNotCreatedException"
        ]
    },
    "CODE_ERR": {
        "name": "Kodlama Hataları",
        "types": [
            "NullPointerException",
            "ArrayIndexOutOfBoundsException",
            "ClassCastException",
            "IllegalArgumentException",
            "NumberFormatException",
            "ConcurrentModificationException"
        ]
    },
    "CONFIG_ERR": {
        "name": "Konfigürasyon Hataları",
        "types": [
            "MissingConfigurationFile",
            "InvalidEnvironmentVariable",
            "IncorrectDriverVersion",
            "MisconfiguredTestSetup",
            "MissingDependencies"
        ]
    },
    "DATA_ERR": {
        "name": "Veri Hataları",
        "types": [
            "TestDataMissing",
            "DataTypeMismatch",
            "ConstraintViolation",
            "DataCorruption",
            "InvalidDataFormat"
        ]
    },
    "DB_ERR": {
        "name": "Veritabanı Hataları",
        "types": [
            "SQLSyntaxErrorException",
            "SQLIntegrityConstraintViolationException",
            "ConnectionPoolExhausted",
            "DeadlockException",
            "QueryTimeoutException"
        ]
    },
    "ENV_ERR": {
        "name": "Çevresel Hatalar",
        "types": [
            "ServerDown",
            "EnvironmentNotReachable",
            "DNSResolutionError",
            "SSLCertificateError",
            "FirewallBlocking"
        ]
    },
    "NET_ERR": {
        "name": "Ağ Hataları",
        "types": [
            "ConnectionReset",
            "SocketTimeoutException",
            "HostUnreachable",
            "ConnectionRefused",
            "NetworkUnreachable"
        ]
    },
    "PERF_ERR": {
        "name": "Performans Hataları",
        "types": [
            "SlowResponseDetected",
            "DatabaseTimeout",
            "APIResponseDelay",
            "MemoryLeakDetected",
            "HighCPUUsage"
        ]
    },
    "SEC_ERR": {
        "name": "Güvenlik Hataları",
        "types": [
            "AuthenticationFailure",
            "AuthorizationFailure",
            "TokenExpired",
            "TokenInvalid",
            "AccessDenied",
            "CSRFValidationFailed"
        ]
    },
    "VERSION_ERR": {
        "name": "Sürüm Uyumsuzluğu Hataları",
        "types": [
            "IncompatibleDriverVersion",
            "UnsupportedBrowserVersion",
            "OutdatedLibrary",
            "APIVersionMismatch",
            "DeprecatedFeature"
        ]
    }
}

def seed_database():
    """Veritabanına başlangıç verilerini yükler"""
    init_db()
    db = SessionLocal()
    
    try:
        # Mevcut verileri kontrol et
        existing = db.query(ErrorCategory).first()
        if existing:
            print("Veritabanı zaten dolu, seed işlemi atlanıyor.")
            return
        
        # Her kategori için veri ekle
        for code, data in ERROR_DATA.items():
            category = ErrorCategory(
                category_code=code,
                category_name=data["name"],
                description=f"{data['name']} kategorisi"
            )
            db.add(category)
            db.flush()  # ID almak için
            
            # Hata tiplerini ekle
            for error_type in data["types"]:
                error = ErrorType(
                    category_id=category.id,
                    error_type=error_type,
                    description=f"{error_type} hatası"
                )
                db.add(error)
        
        db.commit()
        print(f"✅ {len(ERROR_DATA)} kategori ve hata tipleri başarıyla eklendi!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Hata: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
