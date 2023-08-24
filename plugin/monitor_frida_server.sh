#!/system/bin/sh

echo "frida-server 监控脚本"

while [ 1 -gt 0 ]; do
  port=$(netstat -nlt | grep 6666 | wc -l)
  if [ $port -ne 1 ]; then
    echo "frida-server 断开连接，正常在启动中...."
    $(cd /data/local/tmp && ./fs1280 -l 0.0.0.0:6666)
  else
    echo "frida-server 正在运行...."
  fi
  sleep 1s
done
