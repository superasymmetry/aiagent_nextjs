Start-VM -Name Windows10VM

Start-Sleep -Seconds 15

Start-Process "vmconnect.exe" -ArgumentList "localhost", "Windows10VM"

Start-Sleep -Seconds 5

Start-Process "python" -ArgumentList "C:\Path\To\vm_input_script.py"