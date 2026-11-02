-- Generated from the Data Dictionary (14 tables). MariaDB 10.6+
SET NAMES utf8mb4;

-- 3.1: ข้อมูลพนักงาน
CREATE TABLE `employees` (
  `emp_id` INT NOT NULL AUTO_INCREMENT COMMENT 'รหัสพนักงาน (ภายในระบบ)',
  `emp_code` VARCHAR(20) NOT NULL COMMENT 'รหัสพนักงานตามบริษัท',
  `fullname` VARCHAR(150) NOT NULL COMMENT 'ชื่อ-สกุล',
  `position` VARCHAR(30) NOT NULL COMMENT 'ตำแหน่ง ได้แก่ ช่าง หัวหน้างาน ผู้ช่วยผู้จัดการ ผู้จัดการ',
  `phone` VARCHAR(20) NULL COMMENT 'เบอร์โทรศัพท์',
  `is_active` TINYINT(1) NOT NULL COMMENT 'สถานะการทำงาน (1 = ปฏิบัติงานอยู่)',
  PRIMARY KEY (`emp_id`),
  UNIQUE KEY `uq_employees_emp_code` (`emp_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3.2: บทบาทผู้ใช้
CREATE TABLE `roles` (
  `role_code` VARCHAR(20) NOT NULL COMMENT 'รหัสบทบาท ได้แก่ ADMIN MANAGER ASSIS SUP ENG',
  `role_name` VARCHAR(50) NOT NULL COMMENT 'ชื่อบทบาท',
  PRIMARY KEY (`role_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3.3: บัญชีผู้ใช้
CREATE TABLE `users` (
  `user_id` INT NOT NULL AUTO_INCREMENT COMMENT 'รหัสบัญชีผู้ใช้',
  `emp_id` INT NOT NULL COMMENT 'รหัสพนักงานเจ้าของบัญชี',
  `username` VARCHAR(50) NOT NULL COMMENT 'ชื่อผู้ใช้สำหรับเข้าสู่ระบบ',
  `password_hash` VARCHAR(255) NOT NULL COMMENT 'รหัสผ่านที่เข้ารหัสแล้ว',
  `role_code` VARCHAR(20) NOT NULL COMMENT 'รหัสบทบาทของบัญชี',
  `is_active` TINYINT(1) NOT NULL COMMENT 'เปิดใช้งานบัญชี',
  `created_at` DATETIME NOT NULL COMMENT 'วันที่สร้างบัญชี',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `uq_users_username` (`username`),
  CONSTRAINT `fk_users_emp_id` FOREIGN KEY (`emp_id`) REFERENCES `employees` (`emp_id`),
  CONSTRAINT `fk_users_role_code` FOREIGN KEY (`role_code`) REFERENCES `roles` (`role_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3.5: ทีม
CREATE TABLE `teams` (
  `team_id` INT NOT NULL AUTO_INCREMENT COMMENT 'รหัสทีม',
  `team_name` VARCHAR(100) NOT NULL COMMENT 'ชื่อทีม',
  `sup_emp_id` INT NOT NULL COMMENT 'รหัสหัวหน้างานของทีม',
  `is_active` TINYINT(1) NOT NULL COMMENT 'เปิดใช้งานทีม',
  PRIMARY KEY (`team_id`),
  UNIQUE KEY `uq_teams_team_name` (`team_name`),
  CONSTRAINT `fk_teams_sup_emp_id` FOREIGN KEY (`sup_emp_id`) REFERENCES `employees` (`emp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3.4: โซน
CREATE TABLE `zones` (
  `zone_id` INT NOT NULL AUTO_INCREMENT COMMENT 'รหัสโซน',
  `zone_name` VARCHAR(100) NOT NULL COMMENT 'ชื่อโซน',
  `team_id` INT NOT NULL COMMENT 'รหัสทีมที่โซนสังกัด',
  `emp_id` INT NOT NULL COMMENT 'รหัสช่างประจำโซน',
  `description` VARCHAR(255) NULL COMMENT 'รายละเอียดพื้นที่ของโซน',
  `is_active` TINYINT(1) NOT NULL COMMENT 'เปิดใช้งานโซน',
  PRIMARY KEY (`zone_id`),
  UNIQUE KEY `uq_zones_zone_name` (`zone_name`),
  UNIQUE KEY `uq_zones_emp_id` (`emp_id`),
  CONSTRAINT `fk_zones_team_id` FOREIGN KEY (`team_id`) REFERENCES `teams` (`team_id`),
  CONSTRAINT `fk_zones_emp_id` FOREIGN KEY (`emp_id`) REFERENCES `employees` (`emp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3.6: ประวัติการย้ายทีมของหัวหน้างาน
CREATE TABLE `team_supervisor_logs` (
  `log_id` INT NOT NULL AUTO_INCREMENT COMMENT 'รหัสรายการย้ายทีม',
  `emp_id` INT NOT NULL COMMENT 'รหัสหัวหน้างานที่ถูกย้าย',
  `prev_team_id` INT NULL COMMENT 'รหัสทีมก่อนหน้า (ว่างไว้ = กำหนดครั้งแรก)',
  `new_team_id` INT NOT NULL COMMENT 'รหัสทีมที่ย้ายไป',
  `changed_at` DATETIME NOT NULL COMMENT 'วันเวลาที่เปลี่ยนทีม',
  PRIMARY KEY (`log_id`),
  CONSTRAINT `fk_team_supervisor_logs_emp_id` FOREIGN KEY (`emp_id`) REFERENCES `employees` (`emp_id`),
  CONSTRAINT `fk_team_supervisor_logs_prev_team_id` FOREIGN KEY (`prev_team_id`) REFERENCES `teams` (`team_id`),
  CONSTRAINT `fk_team_supervisor_logs_new_team_id` FOREIGN KEY (`new_team_id`) REFERENCES `teams` (`team_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3.7: ประเภทอุปกรณ์
CREATE TABLE `product_types` (
  `type_id` INT NOT NULL AUTO_INCREMENT COMMENT 'รหัสประเภทอุปกรณ์',
  `type_name` VARCHAR(50) NOT NULL COMMENT 'ชื่อประเภท ได้แก่ Router, Switch, UPS, LAN Cable และ Access Point',
  PRIMARY KEY (`type_id`),
  UNIQUE KEY `uq_product_types_type_name` (`type_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3.8: รุ่นอุปกรณ์
CREATE TABLE `products` (
  `product_id` INT NOT NULL AUTO_INCREMENT COMMENT 'รหัสรุ่นอุปกรณ์',
  `type_id` INT NOT NULL COMMENT 'รหัสประเภทอุปกรณ์',
  `brand` VARCHAR(50) NULL COMMENT 'ยี่ห้อ',
  `model_name` VARCHAR(100) NOT NULL COMMENT 'ชื่อรุ่น',
  PRIMARY KEY (`product_id`),
  UNIQUE KEY `uq_products_model_name` (`model_name`),
  CONSTRAINT `fk_products_type_id` FOREIGN KEY (`type_id`) REFERENCES `product_types` (`type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3.9: สถานะอุปกรณ์
CREATE TABLE `spare_statuses` (
  `status_code` VARCHAR(20) NOT NULL COMMENT 'รหัสสถานะ',
  `status_name` VARCHAR(50) NOT NULL COMMENT 'ชื่อสถานะ เช่น รอแจกจ่าย พร้อมใช้ ชำรุด ส่งซ่อม',
  `step_no` INT NOT NULL COMMENT 'ลำดับขั้นของสถานะ',
  `description` VARCHAR(255) NULL COMMENT 'คำอธิบายสถานะ',
  PRIMARY KEY (`status_code`),
  UNIQUE KEY `uq_spare_statuses_status_name` (`status_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3.10: อุปกรณ์อะไหล่รายเครื่อง
CREATE TABLE `spares` (
  `spare_id` INT NOT NULL AUTO_INCREMENT COMMENT 'รหัสอุปกรณ์รายเครื่อง',
  `serial_number` VARCHAR(50) NOT NULL COMMENT 'หมายเลขเครื่อง (Serial Number)',
  `product_id` INT NOT NULL COMMENT 'รหัสรุ่นอุปกรณ์',
  `status_code` VARCHAR(20) NOT NULL COMMENT 'รหัสสถานะปัจจุบัน',
  `emp_id` INT NULL COMMENT 'รหัสช่างผู้ถือครองปัจจุบัน (ว่างไว้เมื่อยังไม่แจกจ่ายหรือส่งซ่อมแล้ว)',
  `store_doc_no` VARCHAR(30) NULL COMMENT 'เลขที่เอกสารรับจากคลังหรือส่งซ่อม',
  `received_date` DATE NULL COMMENT 'วันที่รับอุปกรณ์จากคลัง',
  `remark` VARCHAR(255) NULL COMMENT 'หมายเหตุ',
  `updated_at` DATETIME NOT NULL COMMENT 'วันเวลาที่ปรับปรุงล่าสุด',
  PRIMARY KEY (`spare_id`),
  UNIQUE KEY `uq_spares_serial_number` (`serial_number`),
  CONSTRAINT `fk_spares_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`),
  CONSTRAINT `fk_spares_status_code` FOREIGN KEY (`status_code`) REFERENCES `spare_statuses` (`status_code`),
  CONSTRAINT `fk_spares_emp_id` FOREIGN KEY (`emp_id`) REFERENCES `employees` (`emp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3.11: การแจกจ่ายอุปกรณ์ให้ช่าง
CREATE TABLE `spare_assignments` (
  `sa_id` INT NOT NULL AUTO_INCREMENT COMMENT 'รหัสรายการแจกจ่าย',
  `spare_id` INT NOT NULL COMMENT 'รหัสอุปกรณ์ที่แจกจ่าย',
  `emp_id` INT NOT NULL COMMENT 'รหัสช่างผู้รับอุปกรณ์',
  `assign_type` VARCHAR(10) NOT NULL COMMENT 'ประเภทการแจกจ่าย ได้แก่ ปกติ หรือ ชดเชย',
  `assigned_at` DATETIME NOT NULL COMMENT 'วันเวลาที่แจกจ่าย',
  `confirmed_at` DATETIME NULL COMMENT 'วันเวลาที่ช่างยืนยันรับ',
  `note` VARCHAR(255) NULL COMMENT 'หมายเหตุ เช่น เลขที่อุปกรณ์ที่ได้รับชดเชย',
  PRIMARY KEY (`sa_id`),
  CONSTRAINT `fk_spare_assignments_spare_id` FOREIGN KEY (`spare_id`) REFERENCES `spares` (`spare_id`),
  CONSTRAINT `fk_spare_assignments_emp_id` FOREIGN KEY (`emp_id`) REFERENCES `employees` (`emp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3.12: การใช้งานอุปกรณ์หน้างาน
CREATE TABLE `spare_usages` (
  `usage_id` INT NOT NULL AUTO_INCREMENT COMMENT 'รหัสรายการใช้งาน',
  `spare_id` INT NOT NULL COMMENT 'รหัสอุปกรณ์ที่นำไปติดตั้ง',
  `removed_spare_id` INT NULL COMMENT 'รหัสอุปกรณ์ที่ถอดคืนจากหน้างาน',
  `emp_id` INT NOT NULL COMMENT 'รหัสช่างผู้ใช้งาน',
  `cid` VARCHAR(50) NOT NULL COMMENT 'รหัสวงจร (Circuit ID)',
  `site_name` VARCHAR(150) NULL COMMENT 'ชื่อสถานที่ติดตั้ง',
  `photo_path` VARCHAR(255) NULL COMMENT 'ที่อยู่ไฟล์รูปหน้างาน',
  `remark` VARCHAR(255) NULL COMMENT 'หมายเหตุ',
  `used_at` DATETIME NOT NULL COMMENT 'วันเวลาที่ใช้งาน',
  PRIMARY KEY (`usage_id`),
  CONSTRAINT `fk_spare_usages_spare_id` FOREIGN KEY (`spare_id`) REFERENCES `spares` (`spare_id`),
  CONSTRAINT `fk_spare_usages_removed_spare_id` FOREIGN KEY (`removed_spare_id`) REFERENCES `spares` (`spare_id`),
  CONSTRAINT `fk_spare_usages_emp_id` FOREIGN KEY (`emp_id`) REFERENCES `employees` (`emp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3.13: ประวัติสถานะอุปกรณ์
CREATE TABLE `spare_status_logs` (
  `log_id` INT NOT NULL AUTO_INCREMENT COMMENT 'รหัสประวัติสถานะ',
  `spare_id` INT NOT NULL COMMENT 'รหัสอุปกรณ์',
  `usage_id` INT NULL COMMENT 'รหัสรายการใช้งานที่เกี่ยวข้อง',
  `prev_status` VARCHAR(20) NULL COMMENT 'รหัสสถานะก่อนเปลี่ยน',
  `status_code` VARCHAR(20) NOT NULL COMMENT 'รหัสสถานะใหม่',
  `symptom` VARCHAR(255) NULL COMMENT 'อาการชำรุด',
  `cause` VARCHAR(255) NULL COMMENT 'สาเหตุการชำรุด',
  `note` VARCHAR(255) NULL COMMENT 'หมายเหตุ เช่น เลขที่เอกสารส่งซ่อม',
  `actor_id` INT NOT NULL COMMENT 'รหัสบัญชีผู้ทำรายการ',
  `logged_at` DATETIME NOT NULL COMMENT 'วันเวลาที่เปลี่ยนสถานะ',
  PRIMARY KEY (`log_id`),
  CONSTRAINT `fk_spare_status_logs_spare_id` FOREIGN KEY (`spare_id`) REFERENCES `spares` (`spare_id`),
  CONSTRAINT `fk_spare_status_logs_usage_id` FOREIGN KEY (`usage_id`) REFERENCES `spare_usages` (`usage_id`),
  CONSTRAINT `fk_spare_status_logs_status_code` FOREIGN KEY (`status_code`) REFERENCES `spare_statuses` (`status_code`),
  CONSTRAINT `fk_spare_status_logs_actor_id` FOREIGN KEY (`actor_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3.14: เกณฑ์ KPI
CREATE TABLE `kpi_settings` (
  `kpi_id` INT NOT NULL AUTO_INCREMENT COMMENT 'รหัสเกณฑ์ KPI',
  `team_id` INT NULL COMMENT 'รหัสทีมที่ใช้เกณฑ์ (ว่างไว้ = ทุกทีม)',
  `type_id` INT NULL COMMENT 'รหัสประเภทอุปกรณ์ที่ใช้เกณฑ์ (ว่างไว้ = ทุกประเภท)',
  `status_code` VARCHAR(20) NOT NULL COMMENT 'รหัสสถานะที่ควบคุมเวลา เช่น ชำรุด',
  `max_days` INT NOT NULL COMMENT 'จำนวนวันสูงสุดที่อยู่ในสถานะนั้นได้',
  `effective_date` DATE NOT NULL COMMENT 'วันที่เริ่มมีผล',
  `end_date` DATE NULL COMMENT 'วันที่สิ้นสุดการใช้เกณฑ์ (ว่างไว้ = ยังมีผล)',
  `set_by` INT NOT NULL COMMENT 'รหัสบัญชีผู้ช่วยผู้จัดการผู้กำหนดเกณฑ์',
  `created_at` DATETIME NOT NULL COMMENT 'วันเวลาที่บันทึกเกณฑ์',
  PRIMARY KEY (`kpi_id`),
  CONSTRAINT `fk_kpi_settings_team_id` FOREIGN KEY (`team_id`) REFERENCES `teams` (`team_id`),
  CONSTRAINT `fk_kpi_settings_type_id` FOREIGN KEY (`type_id`) REFERENCES `product_types` (`type_id`),
  CONSTRAINT `fk_kpi_settings_status_code` FOREIGN KEY (`status_code`) REFERENCES `spare_statuses` (`status_code`),
  CONSTRAINT `fk_kpi_settings_set_by` FOREIGN KEY (`set_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

