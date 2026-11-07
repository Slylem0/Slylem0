"""Fetch my public GitHub activity into data.json for the profile generators.

Needs GITHUB_TOKEN (the Actions token is enough). Stdlib only.
Usage: python scripts/fetch.py <login> <out.json>
"""
import json, os, sys, urllib.request
from datetime import date

LOGIN, OUT = sys.argv[1], sys.argv[2]
TOKEN = os.environ["GITHUB_TOKEN"]


def call(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"bearer {TOKEN}", "User-Agent": "profile-gen",
                                          "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


q = """query($l:String!){ user(login:$l){
  contributionsCollection{ contributionCalendar{ totalContributions
    weeks{ contributionDays{ date contributionCount contributionLevel } } } }
  repositories(ownerAffiliations:OWNER, privacy:PUBLIC){ totalCount }
  followers{ totalCount } } }"""
u = call("https://api.github.com/graphql", {"query": q, "variables": {"l": LOGIN}})["data"]["user"]
cal = u["contributionsCollection"]["contributionCalendar"]
LV = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
weeks = [[[d["date"], d["contributionCount"], LV[d["contributionLevel"]]] for d in w["contributionDays"]]
         for w in cal["weeks"]]

days = [d for w in weeks for d in w]
today = date.today().isoformat()
streak = 0
for d, n, _ in reversed([d for d in days if d[0] <= today]):
    if n > 0:
        streak += 1
    elif d != today:          # today may still be empty
        break
best = run = 0
for _, n, _ in days:
    run = run + 1 if n else 0
    best = max(best, run)

# Latest commits of mine across my most recently pushed public repos.
q2 = """query($l:String!){ user(login:$l){ repositories(first:8, privacy:PUBLIC, ownerAffiliations:OWNER,
  orderBy:{field:PUSHED_AT, direction:DESC}){ nodes{ name defaultBranchRef{ target{ ... on Commit{
  history(first:3){ nodes{ oid messageHeadline committedDate author{ user{ login } } } } } } } } } } }"""
commits = []
for r in call("https://api.github.com/graphql", {"query": q2, "variables": {"l": LOGIN}})["data"]["user"]["repositories"]["nodes"]:
    if r["name"] == LOGIN or not r["defaultBranchRef"]:
        continue
    for c in r["defaultBranchRef"]["target"]["history"]["nodes"]:
        if (c["author"]["user"] or {}).get("login") != LOGIN or c["messageHeadline"].startswith("Merge "):
            continue
        commits.append({"sha": c["oid"][:7], "repo": r["name"], "msg": c["messageHeadline"], "date": c["committedDate"]})
commits.sort(key=lambda c: c["date"], reverse=True)

json.dump({"login": LOGIN, "total": cal["totalContributions"], "streak": streak, "best": best,
           "repos": u["repositories"]["totalCount"], "followers": u["followers"]["totalCount"],
           "weeks": weeks, "commits": commits[:4], "generated": today}, open(OUT, "w"), indent=1)
print(f"{OUT}: {cal['totalContributions']} contributions, streak {streak}, best {best}, {len(commits[:4])} commits")
