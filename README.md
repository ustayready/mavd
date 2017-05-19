# mavd
Mobile Application Vulnerability Detection
-
Receives a domain or APK name from CLI, identifies most applications tied to the domain and downloads the APK(s) locally. It then reverses the APK to a jar file using dex2jar, extracts the class files and objects then searches the code for 'secret' type keywords and URLs.
