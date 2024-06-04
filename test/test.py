#!/usr/bin/env python3
#
# This is an example of sending DNS queries over HTTPS (DoH) with dnspython.
import httpx

import dns.message
import dns.query
import dns.rdatatype

# pip install httpx[http2]
# pip install dnspython[doh]


def main():
    where = "https://dns.mullvad.net/dns-query"
    qname = "youtube.com"
    with httpx.Client(http2=True) as client:
        q = dns.message.make_query(qname, dns.rdatatype.A)
        r = dns.query.https(q, where, session=client)
        for answer in r.answer:
            print(answer)

        # ... do more lookups


if __name__ == "__main__":
    main()
