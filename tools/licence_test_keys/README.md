# TEST keys only

`TEST-ONLY-private.pem` signs the licences the tests use (`tools/licence_reference.py`). It is public, in this
repository: a licence signed with it proves nothing. The production key pair is made on the Imagery License Server,
whose private key never leaves it; before release, `LICENCE_PUBLIC_KEY` in `src/AppBuilder/Licence.incl` is replaced
with the production public key.
