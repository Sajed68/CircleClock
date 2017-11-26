### پیش‌نیازها:
<p dir=rtl>
برای اجرای این برنامه می‌توانید از هر دو نسخه python2.7 و python3.6 استفاده نمایید. اما برای اجرای آن باید پیشنیازهای آن را از قبل نصب کنید. پیشنیازها عبارتند از کتابخانه‌های زیر:
</p>  

> * PyQt5
> * lxml
> * requests  
> * Python Imaging Library (PIL)
  
  ### نصب روی گنو/لینوکس- اوبونتو:

 <p dir=rtl>
همه کتابخانه‌های مورد نیاز  برای اجرای این ساعت در مخازن اوبونتو موجود هستند و به سادگی می‌توان با استفاده از مدیر بسته apt آن‌ها  را نصب کرد. 
برای اجرای ساعت بر روی سایر توزیع‌ها می‌توانید از مدیر بسته آن توزیع استفاده کنید. 
  سه خط زیر برای نصب پیشنیازها برای python2.7 می‌باشد.
</p>

> $ sudo apt install python-qt5  
> $ sudo apt install python-lxml  
> $ sudo apt install python-requests  

<p dir=rtl>
  برای اجرای آن به مسیر اصلی برنامه رفته:
</p>
  
  > $ python circleclock.py
  
  > $ python3 circleclock.py

### نصب بروی ویندوز و پکیج conda:

<p dir=rtl align=right> 
پیشنهاد می‌کنم اگر می‌خواهید پایتون را بر روی ویندوز نصب کنید، بجای آن از مجموعه
<a href="https://www.anaconda.com/download">Anaconda</a>
استفاده کنید. اما با توجه به این که حجم این بسته زیاد است می‌توانید از جایگزین
ساده‌ی آن یعنی
<a href="https://conda.io/miniconda.html">miniconda</a>  استفاده کنید.
حتما توجه کنید که هنگام نصب گزینه‌های اضافه کردن به مسیرهای سیستم و نیز جایگزینی به عنوان پایتون پیشفرض انتخاب شوند. 
پس از نصب کوندا برروی سیستم می‌تواند با استفاده از دستورات زیر پیشنیازهای برنامه را نصب کنید.
</p>

> conda install qt5  
> conda install pillow  
> pip install lxml  
> pip install request  

<p dir=rtl>
برای این که بتوانید برنامه ساعت را در هنگام راه‌اندازی ویندوز اجرا نمایید باید اول درون پوشه ساعت یک فایل با پسوند clock.bat و با محتوی  ایجاد کنید:
</p>

> python -u circleclock.py

<p dir=rtl>
و نیز یک برنامه راه انداز با پسوند vbs و محتوی زیر ایجاد کنید:
</p>

> Set WshShell = CreateObject("WScript.Shell")   
> WshShell.Run chr(34) & "clock.bat" & Chr(34), 0  
> Set WshShell = Nothing  

<p dir=rtl>
سپس یک میانبر از فایل با پسوند vbs را درون پوشه startup ویندوز قرار دهید.
برای بار کردن این پوشه کلید پنجره و R را فشار دهید و در پنجره باز شده عبارت زیر ر وارد نمایید:
</p>

> shell:startup

