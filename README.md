# Protocol deviation datasets

This repository contains data from multiple MRI scanning sessions,
wherein a plethora of deviations from the expected acquisition protocol have been introduced.
It is intended to be used in demonstration of the "ProtocolQC by Florey" tool:
https://github.com/Australian-Epilepsy-Project/protocol_qc

## Adding datasets

Addition of datasets to the repository should conform to the following:

1.  Choose a suitable unique name for the data from that session.

    For data collected thus far for this purpose,
    at the scanner console the subject has been given a first name of "`PHANTOM`"
    and surname corresponding to the unique index of that session;
    that unique index has also been appended to the session protocol name.
    This is however not compulsory;
    it simply acts as a sanity check for data curation.

2.  Run `convert.py` on the DICOM data obtained from the scanner,
    saving into a directory named based on the chosen unique identifier.
    This command anonymises the data,
    and reduces the storage space required by erasing pixel data
    and large private vendor-specific metadata.

3.  Having obtained a PDF printout of the MRI session protocol from the scanner console,
    save that file within the directory of that session with the name "`protocol.pdf`".

4.  Create a commit adding the new directory to the repository.

5.  Push the addition to GitHub.
