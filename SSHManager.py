#!/usr/bin/python

import paramiko
import sys
import os, sys, subprocess
from subprocess import Popen,PIPE, STDOUT
import logging
import time

logging.getLogger("paramiko").setLevel(logging.ERROR)

#paramiko.util.log_to_file('paramiko.log')
class ssh:
    def __init__(self, address, username="root"):
        self.address = address
        self.username = username


    def _cmd_collector(method):
        def warpper(*args):
            with open('/tmp/oneclick_executed_cmd.txt', 'a') as f:
                f.write('{0}={1}\r\n'.format(args[0].address, args[1]))
            #method(args[0], args[1])

        return warpper

    @_cmd_collector
    def ssh_connect(self, timeout):
        try:
            print("Connecting to server." + self.address)
            self.client = paramiko.SSHClient()
            self.timeout = timeout
            # Add the policy
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(hostname=self.address, timeout=self.timeout, username=self.username)
            # print("Successfully opened SSH connection")
            return True
        except Exception as e:
            print('Connection Failed')
            print(e)
            return False

    @_cmd_collector
    def ssh_command(self, command):
        output_list = []
        shell = self.client.invoke_shell()
        stdin, stdout, stderr = self.client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        # print(stdout.read())
        if exit_status > 0:
            for output in stderr.readlines():
                output_list.append(output)
        else:
            for output in stdout.readlines():
                output_list.append(output)
        # print "Command done, closing shell"
        shell.close()
        return exit_status, output_list

    #@_cmd_collector
    def ssh_command_exec(self, command, timeout):
        #custom exception class
        class TimeoutError(Exception):
            pass

        try:
            #create SSH client object
            self.client = paramiko.SSHClient()
            self.timeout = timeout
            # Add missting host key policy
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            #client connect to host
            self.client.connect(hostname=self.address, timeout=30, username=self.username)
            output_list = []
            #invoke the shell
            shell = self.client.invoke_shell()
            #print(command)
            #execute the command and receive stdin, stdout and stderr
            stdin, stdout, stderr = self.client.exec_command(command)
            start = time.time()
            counter = start
            #loop till timeout
            while (self.timeout >= int(counter) - int(start)):
                #add one second sleep
                time.sleep(1)
                #if remote process exited and return an exit status
                if (stdout.channel.exit_status_ready()):
                    #receive exit status 0 for success and greater then zero for failure
                    exit_status = stdout.channel.recv_exit_status()
                    #handling failure case
                    if exit_status > 0:
                        output = '\n'.join(stderr.readlines())
                        output = output + '\n'.join(stdout.readlines())
                    #handling success case
                    else:
                        output = '\n'.join(stdout.readlines())
                    shell.close()
                    return exit_status, output
                else:
                    time.sleep(2)
                    counter = time.time()
                #if wait time increased as compare to timeout then close shell 
                if (self.timeout < int(counter) - int(start)):
                    shell.close()
                    raise TimeoutError()
        except TimeoutError:
            print('SSH TIMEOUT!!')
            return 1, str('SSH TIMEOUT!!')
        except Exception as e:
            print(self.address + ': SSH Connection Failed. Reason - ' + str(e))
            return 1, str(e)


    def closeConnection(self):
        if (self.client != None):
            self.client.close()


    def send_file(self, sourcefile, destfile, timeout):
        try:
            self.client = paramiko.SSHClient()
            self.timeout = timeout
            # Add the policy
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(hostname=self.address, timeout=self.timeout, username=self.username)
            sftp = self.client.open_sftp()
            sftp.put(sourcefile, destfile)
            sftp.close()
            self.client.close()
            return 0, "SUCCESS"
        except Exception as e:
            print "Error in sending file. Error:", e
            return 1, str(e)


    def receive_file(self, sourcefile, destfile, timeout):
        try:
            #create ssh client object
            self.client = paramiko.SSHClient()
            self.timeout = timeout
            # Add missing host key policy, passing the paramiko AutoAddPolicy() object
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            #call connect method and provided host, timeout, username, password
            self.client.connect(hostname=self.address, timeout=self.timeout, username=self.username)
            #open sftp session
            sftp = self.client.open_sftp()
            #get the file
            sftp.get(sourcefile, destfile)
            #close the connection
            sftp.close()
            self.client.close()
            return 0, "SUCCESS"
        except Exception as e:
            print "Error in receiving file. Error:", e
            return 1, str(e)

