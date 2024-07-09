import pymysql
import subprocess
import pexpect
import time

def start_mysql_service():
    # 检查MySQL服务是否在运行
    try:
        service_status = subprocess.check_output("ps aux | grep mysqld", shell=True)
        if b"mysqld" in service_status and b"/usr/local/mysql/bin/mysqld" in service_status:
            print("MySQL服务已经在运行")
            return True
    except subprocess.CalledProcessError:
        print("MySQL服务未运行，尝试启动...")

    # 启动MySQL服务
    sudo_password = '246859'  # 替换为你的sudo密码
    command_start = f"echo {sudo_password} | sudo -S /usr/local/mysql/support-files/mysql.server start"

    try:
        pexpect.run(command_start)
        print("MySQL服务启动成功")
        return True
    except Exception as e:
        print("启动MySQL服务失败: " + str(e))
        return False

def is_mysql_running():
    try:
        service_status = subprocess.check_output("launchctl list | grep com.oracle.oss.mysql.mysqld", shell=True)
        if b"com.oracle.oss.mysql.mysqld" in service_status:
            return True
        return False
    except subprocess.CalledProcessError:
        return False

def check_mysql_log():
    sudo_password = '246859'  # 替换为你的sudo密码
    command_log = f"echo {sudo_password} | sudo -S tail -n 20 /usr/local/mysql/data/your_mysql_log.err"

    try:
        log_output = subprocess.check_output(command_log, shell=True).decode('utf-8')
        print("MySQL日志输出:\n", log_output)
    except subprocess.CalledProcessError as e:
        print("无法读取MySQL日志: " + str(e))
def db_connect():
    """
    连接到MySQL数据库
    此函数使用提供的主机、用户、密码和数据库名称连接到MySQL数据库。它返回一个游标对象以执行数据库操作以及数据库连接对象。
    返回:
        cur (pymysql.cursors.Cursor): 用于与数据库交互的游标对象。
        db (pymysql.connections.Connection): 数据库连接对象。
    """
    DBHOST = "localhost"
    DBUSER = "root"
    DBPASS = "GYZ1998*"
    DBNAME = "ALPR"
    # if not start_mysql_service():
    #     print("无法连接到数据库，因为MySQL服务未启动")
    #     return None, None
    #
    # # 等待MySQL服务完全启动
    # time.sleep(5)
    # # 确保MySQL服务在运行
    # # 确保MySQL服务在运行
    # if not is_mysql_running():
    #     print("MySQL服务未运行，无法连接到数据库")
    #     check_mysql_log()
    #     return None, None

    try:
        db = pymysql.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME, charset="utf8", port=3306)
        print("数据库连接成功")
    except pymysql.Error as e:
        print("数据库连接失败" + str(e))

    cur = db.cursor()
    return cur, db

def show_all_data(cur):
    """
        显示所有数据库表中的数据
        此函数从指定的数据库游标对象中查询表 "plate_pay" 中的所有数据，并返回查询结果。
        参数:
            cur (pymysql.cursors.Cursor): 用于与数据库交互的游标对象。
        返回:
            results (tuple): 查询到的所有数据。
        """
    SqlQuery = "SELECT * FROM plate_pay"
    # 查询表中所有数据
    try:
        cur.execute(SqlQuery)
        results=cur.fetchall()
    #     for row in results:
    #         id = row[0]
    #         plate_number = row[1]
    #         enter_time = row[2]
    #         exit_time = row[3]
    #         payment_amount = row[4]
    #         payment_status = row[5]
    #         print("id:%s, plate_number:%s, enter_time: %s, exit_time: %s, payment_amount: %s, payment_status:%s"%(id, plate_number, enter_time, exit_time, payment_amount, payment_status))
    except pymysql.Error as e:
        print("数据查询失败："+str(e))
    return  results

def insert_in(cur, db, plate_result, time, payment_status=0):
    """
        插入数据到数据库表中
        此函数将车牌号、进入时间和支付状态插入到指定的数据库表 "plate_pay" 中。
        参数:
            cur (pymysql.cursors.Cursor): 用于与数据库交互的游标对象。
            db (pymysql.connections.Connection): 与数据库的连接对象，用于提交或回滚事务。
            plate_result (str): 车牌号。
            time (str): 车辆进入时间。
            payment_status (int, 可选): 支付状态，默认为0。
        返回:
            None
        异常:
            pymysql.Error: 如果插入数据时出现任何错误，将打印错误信息并回滚事务。
        """
    sqlQuery = " INSERT INTO plate_pay (plate_number, enter_time, payment_status) VALUE (%s,%s, %s) "
    value = (plate_result, time, bool(payment_status))
    try:
        cur.execute(sqlQuery, value)
        db.commit()
        print('数据插入成功！')
    except pymysql.Error as e:
        print("数据插入失败：" + e)
        db.rollback()


# 原先入库的时候没有出库时间和消费金额信息，且payment_status为0,现更新数据
def insert_out(cur, db, id, time, payment, payment_status=1):
    """
    更新数据库表中的记录
    此函数更新指定记录的离开时间、支付金额和支付状态。
    参数:
        cur (pymysql.cursors.Cursor): 用于与数据库交互的游标对象。
        db (pymysql.connections.Connection): 与数据库的连接对象，用于提交或回滚事务。
        id (int): 要更新的记录的唯一标识符（如主键）。
        time (str): 车辆离开时间。
        payment (float): 支付金额。
        payment_status (int, 可选): 支付状态，默认为1。
    返回:
        None
    异常:
        Exception: 如果更新记录时出现任何错误，将打印错误信息并回滚事务。
    """
    try:
        # 更新记录的SQL语句，其中id为要更新的记录的唯一标识符（如主键）
        sql = "UPDATE plate_pay SET exit_time=%s, payment_amount=%s, payment_status=%s WHERE id=%s"
        values = (time, payment, payment_status, id)
        cur.execute(sql, values)
        db.commit()  # 确保更改被提交到数据库
        print("记录已成功更新")
    except Exception as e:
        print("更新记录时出错:", e)
        db.rollback()  # 回滚事务，撤销任何未提交的更改


# 根据车牌号得到当前尚未出库的数据库记录
def get_not_out(cur, plate_number):
    sql = "SELECT * FROM plate_pay WHERE plate_number=%s AND payment_status=%s"
    params = (plate_number, bool(0))
    try:
        cur.execute(sql, params)

        # 获取结果集
        result = cur.fetchall()

        return result

    except Exception as e:
        print("Error: ", str(e))

# 获取所有未出库的数据库记录
def not_out_all(cur):
    """
        查询所有未支付的记录
        此函数从数据库中查询所有payment_status为0的记录。
        参数:
            cur (pymysql.cursors.Cursor): 用于与数据库交互的游标对象。
        返回:
            tuple: 查询到的所有记录。如果查询失败，返回None。
        异常:
            Exception: 如果查询过程中出现任何错误，将打印错误信息。
        """
    sql = "SELECT * FROM plate_pay WHERE payment_status=%s"
    params = (bool(0))
    try:
        cur.execute(sql, params)

        # 获取结果集
        result = cur.fetchall()

        return result

    except Exception as e:
        print("Error: ", str(e))