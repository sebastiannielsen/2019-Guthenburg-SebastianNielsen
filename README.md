# openhack
Openhack-2019-Guthenburg

REQUIRES: A folder called "openaid" containing CSVs from OpenAid.

REQUIRES: cpi.csv, which is the Corrupton Perception Index file (xls) saved as CSV.

No changes required to the CSVs, the scripts will automatically "scrub" them from any faulty data when loading them.

index.cgi: Main script

install.cgi: Is used after installing cpi.csv, you must click the indicated country to "register" it in data.txt, until no more countries are being asked for.

If country is not available in world.png, it might be too small - enlarge the country in MS Paint.
(No, your'e not changing the world :-), its just that the map needs to be more coarse to convey the information)

*** SECURITY WARNING ***

These scripts are designed to run on a CLOSED webserver NOT available for the public. The scripts aren't secure enough for public use.
(ergo, the webserver can be taken over).
Due to time constraints, certain security controls have not been implemented, but can be easily implemented.
