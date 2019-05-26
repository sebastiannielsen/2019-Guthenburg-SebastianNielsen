# openhack
Openhack-2019-Guthenburg. My submission for the "SIDA" challenge.

REQUIRES: A folder called "openaid" containing CSVs from OpenAid.

REQUIRES: cpi.csv, which is the Corrupton Perception Index file (xls) saved as CSV.

No changes required to the CSVs, the scripts will automatically "scrub" them from any faulty data when loading them.

index.cgi: Main script

install.cgi: Is used after installing cpi.csv, you must click the indicated country to "register" it in data.txt, until no more countries are being asked for.

If country is not available in world.png, it might be too small - enlarge the country in MS Paint.
(No, your'e not changing the world :-), its just that the map needs to be more coarse to convey the information)

-----------------------------------------------------------------------

The whole system works like a scale, but with data. You "weight" data against each other, and the scale will "weight" against red, blue, or if the scale is in center position, green.

In this case, I have made the scale to use the colors red, green and blue. Since a high corruption index is "good" (0 = corrupt, 100 = clean), I have made so the scale shows a redish value for a corrupt country that receives much donations, a green value for a corrupt country that receives no money (no weights on both sides of a scale would of course cause it to go center), and bluish color for a more cleanish country that receives no money.
You can also invert the "money" parameter, so a country that receives LESS money gets heavier on the "money" side. That can be a good idea to do sometimes.

Each CSV file represent different sectors, but of course, the script can be loaded with any CSV files from OpenAid, even for example different CSV files combined.

The whole idea of the script, is to act as a visual "data laboratory" for corruption and donations against each other, so any strong correlations or anti-correlations are found. For example, if a data source would result in the whole world becoming green, it would indicate a very strong correlation, because it would mean that weights are added to both sides of the scale at the same time.

While a totally random red/blue scattering, with strong colors, would indicate a strong anti-correlation, where it can be a good idea to "invert" one side. and try it would and see if any patterns emerge. Single colors, like large parts blue or red also indicate a slight correlation.

The idea of the whole script is to play around with the data and using human pattern recongnitzionn to find weak/strong correlations/anticorrelations with the data. Of course, the script could be extended with functions for, to example mix different CSV files together.

---------------------------------------------------------------------------------------

NOTE: The map ONLY colors countries that are available in both data sources. Because, the script
would make NO sense if you don't place anything on one side of the scale. Then you are either only measuring
corruption index OR donation amount, and then you could aswell use OpenAid or Transparency Internation data
directly.

*** SECURITY WARNING ***

These scripts are designed to run on a CLOSED webserver NOT available for the public. The scripts aren't secure enough for public use.
(ergo, the webserver can be taken over).
Due to time constraints, certain security controls have not been implemented, but can be easily implemented.
