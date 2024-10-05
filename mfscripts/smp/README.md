# SMP hand generators

J. and I are learning Standard Modern Precision.
There are a bunch of scenarios that are (sometimes significantly) different from
the older Precisions we knew. It would be nice to practise bidding these hands until
we know we have them right.

BBO's dealer script works - but it's REALLY frustrating (no variables, no actions).
I have a dealer that works, in a language I actually understand.

So I can generate hundreds of hands at a time on very specific structures.

I expect this to be a work in progress, for quite some time...
but it's a good example for other bidding practise.

## Creating, converting and loading the hands into BBO

BBO is also very old, and a bit creaky.
As such it doesn't take PBN, the file format everybody else uses.
So here's how to get some hands in to load in a bidding table:

1. Run the dealer script, generating a PBN file.
    - Note: for some reason, "print"ing the output to a file puts it in UTF16-BOM
      encoding, which absolutely breaks the PBN-to-LIN converter in the next step.
    - Therefore, you *must* write to file, opened with `encoding="utf-8"`.
    - Also note that *all* values must be of the format [Tag "Value"]
2. Upload the PBN file to [Bridgewebs' PBN to LIN converter.](https://dds.bridgewebs.com/pbntolin/ConvertPbnToLin.php)
3. Download the converted file, and check to ensure it actually has hands.
4. Log in to BBO, go to `Account`, then `Deal archive`.
5. Press the "+" button on `Select Folder` to create a new folder for the hands.
   Use the pencil to edit the name of the folder.
    - Note: there are no subfolders. Each folder can only contain hands.
6. Use the `Import LIN File` button to load the downloaded LIN file.
7. In the bidding table, hamburger menu, select `Deal Source`, `Use saved deals`,
   then click on the folder and `Select` it.

Okay, so it's not *much* easier than putting the scripts in Advanced, but it is
easier - and *much* easier to debug. Of course, when you run out of hands, you have to
create and process a whole new set...

## Structure of the files here

- [smp_definitions.py]() is where all the shapes are,
  and all the tests (is it a 1C opener?), and any other utility functions.
- The individual files (like [smp_1d.py]()) have a pretty simple structure:
    - Put "tweaks" at the top so they can be quickly massaged.
    - If there's any custom test, that goes next.
    - Deal accept function (which will use all the above).
    - if there's a condition that is suitable for a predeal (especially a SmartStack),
      put it next. Remember this is a dict: {"<seat>": <condition>}
    - then make a file, and:

```python
with Path(file).open(encoding="utf-8", mode="w") as f:
    generate_and_print_hands(
        f,
        accept,  # the accept function
        predeal=predeal,  # if you have one, else None
        num_hands=int,  # default 100
        alternate_after=int,  # if < num_hands, rotates 180 degrees every N.
    )
```

- generate_and_print_hands is designed specifically for bidding tables, so
  South is dealer every hand.
- If alternate_after, North gets to be dealer half the time.
    - When he is, his hands
      will match the same criteria as *South's hand* when he's dealer - and vice versa.
    - This simulates the effect of switching seats so that
      "I get to open for a bit and you answer."