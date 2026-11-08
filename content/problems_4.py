"""Blind 75, part 4: Dynamic Programming → Bit Manipulation (problems 49–75)."""
from common import E, P, rand_ints, rand_str

# ================================================== 1-D Dynamic Programming

P(id=49, slug="climbing-stairs", title="Climbing Stairs", lc=70, difficulty="Easy", category="1-D Dynamic Programming",
  method="climbStairs", params=["n"],
  description="""You're climbing a staircase with `n` steps. Each move, you can climb either **1 or 2** steps.

How many distinct ways can you reach the top?""",
  examples=[E(2, out=2, why="1 + 1, or 2."), E(3, out=3, why="1 + 1 + 1, 1 + 2, or 2 + 1.")],
  constraints=["1 <= n <= 45"],
  starter='''class Solution:
    def climbStairs(self, n: int) -> int:
        pass
''',
  hints=["Think about your very last move onto step n. Where could you have been just before it?",
         "You arrived from step n−1 (a 1-step) or step n−2 (a 2-step), so `ways(n) = ways(n-1) + ways(n-2)`. Look familiar? 🐇",
         "Bottom-up with two variables: `a, b = 1, 1` (ways to reach steps 0 and 1). Repeat `n - 1` times: `a, b = b, a + b`. Return `b`. (Plain recursion without memoization is too slow!)"],
  solution=r'''class Solution:
    def climbStairs(self, n: int) -> int:
        a, b = 1, 1
        for _ in range(n - 1):
            a, b = b, a + b
        return b
''',
  complexity="O(n) time, O(1) space",
  gen=lambda r: [[1], [4], [5], [10], [20], [35], [44], [45]])


P(id=50, slug="house-robber", title="House Robber", lc=198, difficulty="Medium", category="1-D Dynamic Programming",
  method="rob", params=["nums"],
  description="""You're a (very polite) robber planning to rob houses along a street. `nums[i]` is the money in house `i`.

The catch: **adjacent houses have connected alarms**, so you can't rob two houses next to each other on the same night. Return the most money you can collect.""",
  examples=[E([1, 2, 3, 1], out=4, why="Rob house 0 (1) and house 2 (3)."),
            E([2, 7, 9, 3, 1], out=12, why="Rob houses 0, 2 and 4: 2 + 9 + 1 = 12.")],
  constraints=["1 <= nums.length <= 100", "0 <= nums[i] <= 400"],
  starter='''class Solution:
    def rob(self, nums: List[int]) -> int:
        pass
''',
  hints=["At each house you have two choices: rob it, or skip it. What does each choice force on its neighbor?",
         "Let `best(i)` = max money from houses `0..i`. Then `best(i) = max(best(i-1), best(i-2) + nums[i])`.",
         "Keep two running values: `prev2` (best up to i−2) and `prev1` (best up to i−1). For each `x`: `prev2, prev1 = prev1, max(prev1, prev2 + x)`. Return `prev1`."],
  solution=r'''class Solution:
    def rob(self, nums: List[int]) -> int:
        prev2 = prev1 = 0
        for x in nums:
            prev2, prev1 = prev1, max(prev1, prev2 + x)
        return prev1
''',
  complexity="O(n) time, O(1) space",
  gen=lambda r: [[[5]], [[2, 1]], [[2, 1, 1, 2]]] + [[rand_ints(r, n, 0, 400)] for n in [4, 8, 15, 50, 100]])


P(id=51, slug="house-robber-ii", title="House Robber II", lc=213, difficulty="Medium", category="1-D Dynamic Programming",
  method="rob", params=["nums"],
  description="""Same polite robber, new street: this time the houses are arranged in a **circle**, so the first house and the last house are neighbors.

Adjacent houses still can't both be robbed. Given `nums`, return the most money you can collect.""",
  examples=[E([2, 3, 2], out=3, why="Houses 0 and 2 are neighbors now, so the best is just house 1."),
            E([1, 2, 3, 1], out=4), E([1, 2, 3], out=3)],
  constraints=["1 <= nums.length <= 100", "0 <= nums[i] <= 1000"],
  starter='''class Solution:
    def rob(self, nums: List[int]) -> int:
        pass
''',
  hints=["The circle only adds one extra rule: you can't rob both the first and the last house.",
         "So either you skip the first house, or you skip the last house. Each of those cases is a straight line — the original House Robber!",
         "Write a helper for the line version. Return `max(nums[0], helper(nums[1:]), helper(nums[:-1]))` — the `nums[0]` handles a single house."],
  solution=r'''class Solution:
    def rob(self, nums: List[int]) -> int:
        def line(houses):
            prev2 = prev1 = 0
            for x in houses:
                prev2, prev1 = prev1, max(prev1, prev2 + x)
            return prev1

        return max(nums[0], line(nums[1:]), line(nums[:-1]))
''',
  complexity="O(n) time, O(1) space",
  gen=lambda r: [[[7]], [[1, 9]], [[200, 3, 140, 20, 10]]] + [[rand_ints(r, n, 0, 1000)] for n in [4, 7, 15, 50, 100]])


P(id=52, slug="longest-palindromic-substring", title="Longest Palindromic Substring", lc=5, difficulty="Medium",
  category="1-D Dynamic Programming", method="longestPalindrome", params=["s"], compare="palindrome",
  description="""Given a string `s`, return the **longest substring** of `s` that is a palindrome (reads the same forwards and backwards).

If there are several of the same maximum length, any of them is accepted.""",
  examples=[E("babad", out="bab", why="\"aba\" is also a valid answer."), E("cbbd", out="bb")],
  constraints=["1 <= s.length <= 1000", "s consists of digits and English letters."],
  starter='''class Solution:
    def longestPalindrome(self, s: str) -> str:
        pass
''',
  hints=["Every palindrome has a center. Instead of checking every substring, what if you grew outward from each possible center?",
         "There are 2n − 1 centers: each character (odd-length palindromes) and each gap between two characters (even-length ones).",
         "For each `i`, expand with `l, r = i, i` and again with `l, r = i, i + 1`: while `l >= 0 and r < len(s) and s[l] == s[r]`, step outward. Track the longest `s[l+1:r]` found."],
  solution=r'''class Solution:
    def longestPalindrome(self, s: str) -> str:
        best = ""
        for i in range(len(s)):
            for l, r in ((i, i), (i, i + 1)):
                while l >= 0 and r < len(s) and s[l] == s[r]:
                    l, r = l - 1, r + 1
                if r - l - 1 > len(best):
                    best = s[l + 1 : r]
        return best
''',
  complexity="O(n²) time, O(1) space",
  gen=lambda r: [["a"], ["ac"], ["aaaa"], ["abacdfgdcaba"]] + [[rand_str(r, n, "ab" if n < 50 else "abc")] for n in [5, 10, 30, 200, 1000]])


P(id=53, slug="palindromic-substrings", title="Palindromic Substrings", lc=647, difficulty="Medium",
  category="1-D Dynamic Programming", method="countSubstrings", params=["s"],
  description="""Given a string `s`, return **how many of its substrings are palindromes**.

Substrings at different positions count separately, even if they contain the same letters.""",
  examples=[E("abc", out=3, why="\"a\", \"b\", \"c\"."), E("aaa", out=6, why="\"a\", \"a\", \"a\", \"aa\", \"aa\", \"aaa\".")],
  constraints=["1 <= s.length <= 1000", "s consists of lowercase English letters."],
  starter='''class Solution:
    def countSubstrings(self, s: str) -> int:
        pass
''',
  hints=["This is a close cousin of 'Longest Palindromic Substring'. Can you reuse the expand-around-center idea?",
         "Every time an expansion step succeeds (`s[l] == s[r]`), you've found one more palindrome.",
         "For each of the 2n − 1 centers, expand outward while the ends match, adding 1 to the count for each successful step."],
  solution=r'''class Solution:
    def countSubstrings(self, s: str) -> int:
        count = 0
        for i in range(len(s)):
            for l, r in ((i, i), (i, i + 1)):
                while l >= 0 and r < len(s) and s[l] == s[r]:
                    count += 1
                    l, r = l - 1, r + 1
        return count
''',
  complexity="O(n²) time, O(1) space",
  gen=lambda r: [["a"], ["ab"], ["aba"]] + [[rand_str(r, n, "ab" if n < 50 else "abc")] for n in [5, 10, 30, 200, 1000]])


def _decode_gen(r):
    cases = [["0"], ["10"], ["100"], ["27"], ["2101"], ["11106"], ["1201234"], ["301"]]
    for n in [5, 10, 20, 40, 90]:
        cases.append(["".join(r.choice("1112226034") for _ in range(n))])
    return cases


P(id=54, slug="decode-ways", title="Decode Ways", lc=91, difficulty="Medium", category="1-D Dynamic Programming",
  method="numDecodings", params=["s"],
  description="""A secret message of letters was encoded as digits using `"A" → "1"`, `"B" → "2"`, …, `"Z" → "26"`.

Given a string of digits `s`, return the **number of ways to decode it** back into letters. Codes like `"06"` are invalid (no leading zeros), so a `0` must be part of `10` or `20`. If there's no valid decoding, return `0`.""",
  examples=[E("12", out=2, why="\"AB\" (1 2) or \"L\" (12)."), E("226", out=3, why="\"BZ\" (2 26), \"VF\" (22 6), or \"BBF\" (2 2 6)."),
            E("06", out=0, why="\"06\" can't be decoded — 6 is \"6\", not \"06\".")],
  constraints=["1 <= s.length <= 100", "s contains only digits and may have leading zeros."],
  starter='''class Solution:
    def numDecodings(self, s: str) -> int:
        pass
''',
  hints=["Read the string left to right. At each spot, you can decode either one digit or two digits. Which choices are allowed?",
         "One digit works if it isn't `'0'`. Two digits work if they form a number from 10 to 26. Let `ways(i)` = number of ways to decode `s[:i]`.",
         "`dp[0] = 1`. For `i` from 1 to n: if `s[i-1] != '0'`, `dp[i] += dp[i-1]`; if `i >= 2` and `10 <= int(s[i-2:i]) <= 26`, `dp[i] += dp[i-2]`. Return `dp[n]` (you can shrink it to two variables)."],
  solution=r'''class Solution:
    def numDecodings(self, s: str) -> int:
        prev2, prev1 = 0, 1  # dp[i-2], dp[i-1]; dp[0] = 1
        for i in range(1, len(s) + 1):
            cur = 0
            if s[i - 1] != "0":
                cur += prev1
            if i >= 2 and 10 <= int(s[i - 2 : i]) <= 26:
                cur += prev2
            prev2, prev1 = prev1, cur
        return prev1
''',
  complexity="O(n) time, O(1) space",
  gen=_decode_gen)


def _coin_gen(r):
    cases = [[[2], 4], [[3, 7], 5], [[186, 419, 83, 408], 6249], [[1, 5, 10, 25], 63], [[2, 5, 10, 1], 27]]
    for k, amount in [(2, 20), (3, 50), (4, 100), (5, 500), (8, 5000)]:
        cases.append([r.sample(range(1, 60), k), amount])
    return cases


P(id=55, slug="coin-change", title="Coin Change", lc=322, difficulty="Medium", category="1-D Dynamic Programming",
  method="coinChange", params=["coins", "amount"],
  description="""You're given coin denominations `coins` and a total `amount`. You have an unlimited supply of each coin.

Return the **fewest coins** needed to make exactly `amount`. If it can't be done, return `-1`.""",
  examples=[E([1, 2, 5], 11, out=3, why="11 = 5 + 5 + 1."), E([2], 3, out=-1), E([1], 0, out=0)],
  constraints=["1 <= coins.length <= 12", "1 <= coins[i] <= 2^31 - 1", "0 <= amount <= 10^4"],
  starter='''class Solution:
    def coinChange(self, coins: List[int], amount: int) -> int:
        pass
''',
  hints=["Greedy (always take the biggest coin) fails — try coins `[1, 3, 4]` with amount 6. Think about the smallest *sub-amounts* instead.",
         "Let `dp[a]` = fewest coins to make amount `a`. If the last coin used is `c`, then `dp[a] = 1 + dp[a - c]`.",
         "`dp = [0] + [inf] * amount`. For `a` from 1 to amount, for each coin `c <= a`: `dp[a] = min(dp[a], dp[a - c] + 1)`. Return `dp[amount]` if it's finite, else -1."],
  solution=r'''class Solution:
    def coinChange(self, coins: List[int], amount: int) -> int:
        dp = [0] + [float("inf")] * amount
        for a in range(1, amount + 1):
            for c in coins:
                if c <= a and dp[a - c] + 1 < dp[a]:
                    dp[a] = dp[a - c] + 1
        return dp[amount] if dp[amount] != float("inf") else -1
''',
  complexity="O(amount · coins) time, O(amount) space",
  gen=_coin_gen)


P(id=56, slug="maximum-product-subarray", title="Maximum Product Subarray", lc=152, difficulty="Medium",
  category="1-D Dynamic Programming", method="maxProduct", params=["nums"],
  description="""Given an integer array `nums`, find the **contiguous subarray** with the largest product, and return that product.""",
  examples=[E([2, 3, -2, 4], out=6, why="[2, 3] has product 6."), E([-2, 0, -1], out=0), E([-2, 3, -4], out=24)],
  constraints=["1 <= nums.length <= 2 * 10^4", "-10 <= nums[i] <= 10", "Every subarray product fits in a 32-bit integer."],
  starter='''class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        pass
''',
  hints=["Unlike sums, a very *negative* product can flip into the very best one when multiplied by another negative.",
         "Track both the largest **and** the smallest product of a subarray ending at each position.",
         "For each `x`: `candidates = (x, x * hi, x * lo)`; `hi, lo = max(candidates), min(candidates)`; `best = max(best, hi)`. Start with `hi = lo = best = nums[0]`."],
  solution=r'''class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        best = hi = lo = nums[0]
        for x in nums[1:]:
            candidates = (x, x * hi, x * lo)
            hi, lo = max(candidates), min(candidates)
            best = max(best, hi)
        return best
''',
  complexity="O(n) time, O(1) space",
  gen=lambda r: [[[-2]], [[0, 2]], [[-1, -1]], [[2, -5, -2, -4, 3]]] + [[rand_ints(r, n, -4, 4)] for n in [5, 8, 15, 25, 30]])


def _wb_gen(r):
    cases = [["a", ["b"]], ["aaaaaaa", ["aaaa", "aaa"]], ["cars", ["car", "ca", "rs"]],
             ["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab", ["a", "aa", "aaa", "aaaa", "aaaaa"]]]
    for nw, parts in [(3, 3), (4, 5), (6, 8), (10, 15)]:
        words = list({rand_str(r, r.randint(1, 4), "abc") for _ in range(nw)})
        s = "".join(r.choice(words) for _ in range(parts))
        if r.random() < 0.5:
            s += r.choice("abcd")
        cases.append([s, words])
    return cases


P(id=57, slug="word-break", title="Word Break", lc=139, difficulty="Medium", category="1-D Dynamic Programming",
  method="wordBreak", params=["s", "wordDict"],
  description="""Given a string `s` and a list of words `wordDict`, return `True` if `s` can be split into a sequence of one or more dictionary words (separated by spaces).

Dictionary words may be reused any number of times.""",
  examples=[E("leetcode", ["leet", "code"], out=True), E("applepenapple", ["apple", "pen"], out=True, why="\"apple pen apple\" — reusing \"apple\" is fine."),
            E("catsandog", ["cats", "dog", "sand", "and", "cat"], out=False)],
  constraints=["1 <= s.length <= 300", "1 <= wordDict.length <= 1000", "1 <= wordDict[i].length <= 20", "All words are unique."],
  starter='''class Solution:
    def wordBreak(self, s: str, wordDict: List[str]) -> bool:
        pass
''',
  hints=["If `s` starts with a dictionary word `w`, then the question becomes: can the *rest* of `s` be broken? That repeats a lot of work — remember the answers.",
         "Let `dp[i]` = `True` if the prefix `s[:i]` can be segmented. `dp[0] = True` (the empty string).",
         "For `i` from 1 to `len(s)`, for each word `w`: if `i >= len(w)` and `dp[i - len(w)]` and `s[i - len(w):i] == w`, set `dp[i] = True`. Return `dp[len(s)]`."],
  solution=r'''class Solution:
    def wordBreak(self, s: str, wordDict: List[str]) -> bool:
        dp = [True] + [False] * len(s)
        for i in range(1, len(s) + 1):
            for w in wordDict:
                if i >= len(w) and dp[i - len(w)] and s[i - len(w) : i] == w:
                    dp[i] = True
                    break
        return dp[len(s)]
''',
  complexity="O(n · m · k) time (m words, k max length), O(n) space",
  gen=_wb_gen)


P(id=58, slug="longest-increasing-subsequence", title="Longest Increasing Subsequence", lc=300, difficulty="Medium",
  category="1-D Dynamic Programming", method="lengthOfLIS", params=["nums"],
  description="""Given an integer array `nums`, return the length of the longest **strictly increasing subsequence**.

A subsequence keeps the original order but may skip elements — e.g. `[3, 6, 2, 7]` is a subsequence of `[0, 3, 1, 6, 2, 2, 7]`.

*Follow-up:* can you do it in O(n log n)?""",
  examples=[E([10, 9, 2, 5, 3, 7, 101, 18], out=4, why="[2, 3, 7, 101] is one longest option."),
            E([0, 1, 0, 3, 2, 3], out=4), E([7, 7, 7, 7, 7, 7, 7], out=1)],
  constraints=["1 <= nums.length <= 2500", "-10^4 <= nums[i] <= 10^4"],
  starter='''class Solution:
    def lengthOfLIS(self, nums: List[int]) -> int:
        pass
''',
  hints=["Let `dp[i]` = length of the longest increasing subsequence that *ends* at index `i`. How does it relate to earlier entries?",
         "`dp[i] = 1 + max(dp[j])` over all `j < i` with `nums[j] < nums[i]` (or just 1). That's O(n²) and totally fine here.",
         "O(n log n) bonus: keep `tails`, where `tails[k]` is the smallest possible tail of an increasing subsequence of length k+1. For each `x`, find `i = bisect_left(tails, x)`; replace `tails[i]` with `x` (or append if `i == len(tails)`). Answer: `len(tails)`."],
  solution=r'''class Solution:
    def lengthOfLIS(self, nums: List[int]) -> int:
        tails = []
        for x in nums:
            i = bisect.bisect_left(tails, x)
            if i == len(tails):
                tails.append(x)
            else:
                tails[i] = x
        return len(tails)
''',
  complexity="O(n log n) time, O(n) space",
  gen=lambda r: [[[1]], [[4, 10, 4, 3, 8, 9]], [[3, 5, 6, 2, 5, 4, 19, 5, 6, 7, 12]]] + [[rand_ints(r, n, -100, 100)] for n in [5, 10, 30, 200, 2500]])

# ================================================== 2-D Dynamic Programming

P(id=59, slug="unique-paths", title="Unique Paths", lc=62, difficulty="Medium", category="2-D Dynamic Programming",
  method="uniquePaths", params=["m", "n"],
  description="""A robot sits in the top-left corner of an `m x n` grid. It can only move **right** or **down**, one cell at a time.

How many different paths can it take to reach the bottom-right corner?""",
  examples=[E(3, 7, out=28), E(3, 2, out=3, why="Right→Down→Down, Down→Down→Right, Down→Right→Down.")],
  constraints=["1 <= m, n <= 100", "The answer is at most 2 * 10^9."],
  starter='''class Solution:
    def uniquePaths(self, m: int, n: int) -> int:
        pass
''',
  hints=["To arrive at a cell, the robot must have come from the cell above it or the cell to its left.",
         "`paths(r, c) = paths(r-1, c) + paths(r, c-1)`, and every cell in the top row or left column has exactly 1 path.",
         "Keep a single row `row = [1] * n`. Repeat `m - 1` times: for `c` in `1..n-1`, `row[c] += row[c - 1]`. Return `row[-1]`. (Math shortcut: `comb(m + n - 2, m - 1)`.)"],
  solution=r'''class Solution:
    def uniquePaths(self, m: int, n: int) -> int:
        row = [1] * n
        for _ in range(m - 1):
            for c in range(1, n):
                row[c] += row[c - 1]
        return row[-1]
''',
  complexity="O(m · n) time, O(n) space",
  gen=lambda r: [[1, 1], [1, 10], [7, 3], [3, 3], [10, 10], [23, 12], [16, 16], [51, 9]])


P(id=60, slug="longest-common-subsequence", title="Longest Common Subsequence", lc=1143, difficulty="Medium",
  category="2-D Dynamic Programming", method="longestCommonSubsequence", params=["text1", "text2"],
  description="""Given two strings `text1` and `text2`, return the length of their **longest common subsequence** (or `0` if they share none).

A subsequence keeps the characters' order but can skip some — `"ace"` is a subsequence of `"abcde"`.""",
  examples=[E("abcde", "ace", out=3, why="\"ace\" is in both."), E("abc", "abc", out=3), E("abc", "def", out=0)],
  constraints=["1 <= text1.length, text2.length <= 1000", "Only lowercase English letters."],
  starter='''class Solution:
    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        pass
''',
  hints=["Compare the strings from the front (or back). If the first characters match, great — what then? If they don't, which character could you drop?",
         "Let `dp[i][j]` = LCS of `text1[i:]` and `text2[j:]`. If `text1[i] == text2[j]`: `1 + dp[i+1][j+1]`. Otherwise: `max(dp[i+1][j], dp[i][j+1])`.",
         "Make a `(len1 + 1) x (len2 + 1)` table of zeros and fill it from the bottom-right corner backward using that rule. The answer is `dp[0][0]`."],
  solution=r'''class Solution:
    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        n1, n2 = len(text1), len(text2)
        dp = [[0] * (n2 + 1) for _ in range(n1 + 1)]
        for i in range(n1 - 1, -1, -1):
            for j in range(n2 - 1, -1, -1):
                if text1[i] == text2[j]:
                    dp[i][j] = 1 + dp[i + 1][j + 1]
                else:
                    dp[i][j] = max(dp[i + 1][j], dp[i][j + 1])
        return dp[0][0]
''',
  complexity="O(n1 · n2) time and space",
  gen=lambda r: [["a", "a"], ["ab", "ba"], ["bsbininm", "jmjkbkjkv"]] + [[rand_str(r, a, "abcd"), rand_str(r, b, "abcd")] for a, b in [(5, 6), (10, 8), (30, 40), (200, 150), (700, 700)]])

# ================================================================== Greedy

P(id=61, slug="maximum-subarray", title="Maximum Subarray", lc=53, difficulty="Medium", category="Greedy",
  method="maxSubArray", params=["nums"],
  description="""Given an integer array `nums`, find the **contiguous subarray** (with at least one number) that has the largest sum, and return that sum.""",
  examples=[E([-2, 1, -3, 4, -1, 2, 1, -5, 4], out=6, why="[4, -1, 2, 1] sums to 6."), E([1], out=1), E([5, 4, -1, 7, 8], out=23)],
  constraints=["1 <= nums.length <= 10^5", "-10^4 <= nums[i] <= 10^4"],
  starter='''class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        pass
''',
  hints=["Walk left to right, keeping a running sum. When would carrying the running sum forward *hurt* you?",
         "If the running sum ever goes negative, it can only drag down whatever comes next — so start fresh. (This is Kadane's algorithm.)",
         "`cur = 0; best = nums[0]`. For each `x`: `cur = max(cur, 0) + x` (drop a negative prefix), then `best = max(best, cur)`. Return `best`."],
  solution=r'''class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        best, cur = nums[0], 0
        for x in nums:
            cur = max(cur, 0) + x
            best = max(best, cur)
        return best
''',
  complexity="O(n) time, O(1) space",
  gen=lambda r: [[[-1]], [[-3, -2, -5]], [[0, -1, 0]]] + [[rand_ints(r, n, -100, 100)] for n in [5, 10, 40, 300, 20000]])


def _jump_gen(r):
    cases = [[[0]], [[1, 0]], [[0, 1]], [[2, 0, 0]], [[1, 1, 0, 1]], [[2, 5, 0, 0]]]
    for n in [5, 10, 30, 200, 10000]:
        cases.append([[r.choice([0, 0, 1, 1, 2, 3]) for _ in range(n)]])
    cases.append([[1] * 10000])
    return cases


P(id=62, slug="jump-game", title="Jump Game", lc=55, difficulty="Medium", category="Greedy",
  method="canJump", params=["nums"],
  description="""You start at index 0 of the array `nums`. Each value `nums[i]` is the **maximum** jump length from that position (you can jump any distance from 0 up to it).

Return `True` if you can reach the last index, otherwise `False`.""",
  examples=[E([2, 3, 1, 1, 4], out=True, why="Jump 1 step to index 1, then 3 steps to the end."),
            E([3, 2, 1, 0, 4], out=False, why="Every route lands on index 3, whose jump length is 0.")],
  constraints=["1 <= nums.length <= 10^4", "0 <= nums[i] <= 10^5"],
  starter='''class Solution:
    def canJump(self, nums: List[int]) -> bool:
        pass
''',
  hints=["You don't need to know *how* to get somewhere — only the farthest index you can possibly reach so far.",
         "Walk forward keeping `reach`, the farthest reachable index. If you ever stand on an index greater than `reach`, you're stuck.",
         "For each `i`: if `i > reach` return `False`; otherwise `reach = max(reach, i + nums[i])`. Return `True` at the end. (Or go backward: move a 'goal' left whenever `i + nums[i] >= goal`, and check if goal hits 0.)"],
  solution=r'''class Solution:
    def canJump(self, nums: List[int]) -> bool:
        reach = 0
        for i, jump in enumerate(nums):
            if i > reach:
                return False
            reach = max(reach, i + jump)
        return True
''',
  complexity="O(n) time, O(1) space",
  gen=_jump_gen)

# =============================================================== Intervals


def _intervals(r, n, hi=100):
    out = []
    for _ in range(n):
        a = r.randint(0, hi)
        out.append([a, a + r.randint(0, hi // 5 + 1)])
    return out


def _disjoint(r, n):
    points = sorted(r.sample(range(0, 200), 2 * n))
    return [[points[2 * i], points[2 * i + 1]] for i in range(n)]


P(id=63, slug="insert-interval", title="Insert Interval", lc=57, difficulty="Medium", category="Intervals",
  method="insert", params=["intervals", "newInterval"],
  description="""You're given a list of **non-overlapping** intervals `intervals`, sorted by start, and one more interval `newInterval = [start, end]`.

Insert `newInterval` so that the list stays sorted and non-overlapping (merge overlaps where needed), and return the result.""",
  examples=[E([[1, 3], [6, 9]], [2, 5], out=[[1, 5], [6, 9]]),
            E([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8], out=[[1, 2], [3, 10], [12, 16]], why="[4,8] overlaps [3,5], [6,7] and [8,10].")],
  constraints=["0 <= intervals.length <= 10^4", "intervals is sorted by start and has no overlaps.", "0 <= start <= end <= 10^5"],
  starter='''class Solution:
    def insert(self, intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:
        pass
''',
  hints=["Every existing interval falls into one of three groups: completely before the new one, overlapping it, or completely after it.",
         "Intervals ending before `newInterval` starts go straight into the result. Overlapping ones get merged into `newInterval` by widening it. Then everything after.",
         "Loop: if `cur[1] < new[0]` append `cur`; elif `cur[0] > new[1]` append `new`, then set `new = cur` (the leftover gets appended at the end); else `new = [min(new[0], cur[0]), max(new[1], cur[1])]`. Finally append `new`."],
  solution=r'''class Solution:
    def insert(self, intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:
        result = []
        new = list(newInterval)
        for cur in intervals:
            if cur[1] < new[0]:
                result.append(cur)
            elif cur[0] > new[1]:
                result.append(new)
                new = cur
            else:
                new = [min(new[0], cur[0]), max(new[1], cur[1])]
        result.append(new)
        return result
''',
  complexity="O(n) time, O(n) space for the output",
  gen=lambda r: [[[], [5, 7]], [[[1, 5]], [2, 3]], [[[1, 5]], [6, 8]], [[[3, 5]], [0, 1]], [[[1, 5]], [0, 5]]]
  + [[_disjoint(r, n), sorted(r.sample(range(0, 210), 2))] for n in [2, 4, 8, 20, 60]])


P(id=64, slug="merge-intervals", title="Merge Intervals", lc=56, difficulty="Medium", category="Intervals",
  method="merge", params=["intervals"], compare="unordered",
  description="""Given an array of `intervals` where `intervals[i] = [start, end]`, **merge all overlapping intervals** and return the non-overlapping intervals that cover the same ranges.

Intervals that just touch (like `[1,4]` and `[4,5]`) count as overlapping.""",
  examples=[E([[1, 3], [2, 6], [8, 10], [15, 18]], out=[[1, 6], [8, 10], [15, 18]]),
            E([[1, 4], [4, 5]], out=[[1, 5]]), E([[4, 7], [1, 4]], out=[[1, 7]])],
  constraints=["1 <= intervals.length <= 10^4", "0 <= start <= end <= 10^4"],
  starter='''class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        pass
''',
  hints=["Overlaps are hard to spot in a random order. What order would put overlapping intervals right next to each other?",
         "Sort by start time. Now each interval either overlaps the *last* merged interval, or starts a new one.",
         "Sort, then for each `[s, e]`: if `result` is non-empty and `s <= result[-1][1]`, set `result[-1][1] = max(result[-1][1], e)`; otherwise append `[s, e]`."],
  solution=r'''class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        intervals.sort(key=lambda iv: iv[0])
        result = []
        for s, e in intervals:
            if result and s <= result[-1][1]:
                result[-1][1] = max(result[-1][1], e)
            else:
                result.append([s, e])
        return result
''',
  complexity="O(n log n) time, O(n) space",
  gen=lambda r: [[[[1, 4]]], [[[1, 4], [0, 0]]], [[[1, 4], [2, 3]]], [[[2, 3], [4, 5], [6, 7], [8, 9], [1, 10]]]]
  + [[_intervals(r, n)] for n in [3, 6, 12, 40, 2000]])


P(id=65, slug="non-overlapping-intervals", title="Non-overlapping Intervals", lc=435, difficulty="Medium", category="Intervals",
  method="eraseOverlapIntervals", params=["intervals"],
  description="""Given an array of `intervals`, return the **minimum number of intervals you need to remove** so that the rest don't overlap.

Intervals that only touch at a point (like `[1,2]` and `[2,3]`) do **not** overlap.""",
  examples=[E([[1, 2], [2, 3], [3, 4], [1, 3]], out=1, why="Remove [1,3] and the rest are fine."),
            E([[1, 2], [1, 2], [1, 2]], out=2), E([[1, 2], [2, 3]], out=0)],
  constraints=["1 <= intervals.length <= 10^5", "-5 * 10^4 <= start < end <= 5 * 10^4"],
  starter='''class Solution:
    def eraseOverlapIntervals(self, intervals: List[List[int]]) -> int:
        pass
''',
  hints=["Flip the question: what's the *maximum* number of intervals you can keep without any overlaps?",
         "Greedy: when two intervals clash, keep the one that **ends earlier** — it leaves the most room for everything after it.",
         "Sort by end time. Track `end` of the last kept interval (start at `-inf`). For each interval: if `start >= end`, keep it (`end = its end`); otherwise count it as removed."],
  solution=r'''class Solution:
    def eraseOverlapIntervals(self, intervals: List[List[int]]) -> int:
        intervals.sort(key=lambda iv: iv[1])
        end = float("-inf")
        removed = 0
        for s, e in intervals:
            if s >= end:
                end = e
            else:
                removed += 1
        return removed
''',
  complexity="O(n log n) time, O(1) extra space",
  gen=lambda r: [[[[1, 100], [11, 22], [1, 11], [2, 12]]], [[[0, 2], [1, 3], [2, 4], [3, 5], [4, 6]]]]
  + [[[[a, a + r.randint(1, 20)] for a in rand_ints(r, n, -100, 100)]] for n in [3, 6, 12, 40, 5000]])


P(id=66, slug="meeting-rooms", title="Meeting Rooms", lc=252, difficulty="Easy", category="Intervals",
  method="canAttendMeetings", params=["intervals"],
  description="""Given an array of meeting time `intervals` where `intervals[i] = [start, end]`, decide whether one person could attend **all** the meetings.

A meeting ending at time `t` and another starting at time `t` don't conflict.""",
  examples=[E([[0, 30], [5, 10], [15, 20]], out=False, why="[0,30] overlaps both other meetings."), E([[7, 10], [2, 4]], out=True)],
  constraints=["0 <= intervals.length <= 10^4", "0 <= start < end <= 10^6"],
  starter='''class Solution:
    def canAttendMeetings(self, intervals: List[List[int]]) -> bool:
        pass
''',
  hints=["If you lined the meetings up in the order they happen, where would a conflict show up?",
         "After sorting by start time, a conflict can only happen between *neighboring* meetings.",
         "Sort by start. For each `i >= 1`, if `intervals[i][0] < intervals[i-1][1]` return `False`. Otherwise return `True`."],
  solution=r'''class Solution:
    def canAttendMeetings(self, intervals: List[List[int]]) -> bool:
        intervals.sort()
        for prev, cur in zip(intervals, intervals[1:]):
            if cur[0] < prev[1]:
                return False
        return True
''',
  complexity="O(n log n) time, O(1) extra space",
  gen=lambda r: [[[]], [[[5, 8]]], [[[5, 8], [8, 9]]], [[[5, 8], [6, 9]]]]
  + [[_disjoint(r, n)] for n in [3, 10, 50]] + [[[[a, a + r.randint(1, 30)] for a in rand_ints(r, n, 0, 500)]] for n in [4, 20]])


P(id=67, slug="meeting-rooms-ii", title="Meeting Rooms II", lc=253, difficulty="Medium", category="Intervals",
  method="minMeetingRooms", params=["intervals"],
  description="""Given an array of meeting time `intervals` where `intervals[i] = [start, end]`, return the **minimum number of conference rooms** needed so every meeting has a room.

A room freed at time `t` can be used by a meeting starting at time `t`.""",
  examples=[E([[0, 30], [5, 10], [15, 20]], out=2), E([[7, 10], [2, 4]], out=1)],
  constraints=["1 <= intervals.length <= 10^4", "0 <= start < end <= 10^6"],
  starter='''class Solution:
    def minMeetingRooms(self, intervals: List[List[int]]) -> int:
        pass
''',
  hints=["The answer is the largest number of meetings happening at the same moment.",
         "Sweep through time: every start needs a room and every end frees one. Sort the start times and end times separately.",
         "Sort `starts` and `ends`. Walk through `starts` with pointer `s` and keep pointer `e` into `ends`: if `starts[s] < ends[e]`, a new room is needed (`rooms += 1`); otherwise a room frees up (`e += 1`). Track the max. (A min-heap of end times also works.)"],
  solution=r'''class Solution:
    def minMeetingRooms(self, intervals: List[List[int]]) -> int:
        starts = sorted(s for s, _ in intervals)
        ends = sorted(e for _, e in intervals)
        rooms = best = 0
        e = 0
        for s in starts:
            if s < ends[e]:
                rooms += 1
            else:
                e += 1
            best = max(best, rooms)
        return best
''',
  complexity="O(n log n) time, O(n) space",
  gen=lambda r: [[[[13, 15], [1, 13]]], [[[1, 5], [8, 10], [2, 9], [3, 4]]], [[[0, 1], [0, 1], [0, 1]]]]
  + [[[[a, a + r.randint(1, 40)] for a in rand_ints(r, n, 0, 200)]] for n in [3, 6, 15, 50, 3000]])

# ========================================================= Math & Geometry


def _matrix(r, rows, cols, lo=-100, hi=100):
    return [rand_ints(r, cols, lo, hi) for _ in range(rows)]


P(id=68, slug="rotate-image", title="Rotate Image", lc=48, difficulty="Medium", category="Math & Geometry",
  method="rotate", params=["matrix"],
  description="""You're given an `n x n` 2D `matrix` representing an image. Rotate it **90 degrees clockwise**, **in place** — modify the input matrix directly instead of creating a new one.

Your function returns nothing; the runner checks the matrix you modified.""",
  examples=[E([[1, 2, 3], [4, 5, 6], [7, 8, 9]], out=[[7, 4, 1], [8, 5, 2], [9, 6, 3]]),
            E([[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]], out=[[15, 13, 2, 5], [14, 3, 4, 1], [12, 6, 8, 9], [16, 7, 10, 11]])],
  constraints=["1 <= n <= 20", "-1000 <= matrix[i][j] <= 1000"],
  starter='''class Solution:
    def rotate(self, matrix: List[List[int]]) -> None:
        """
        Do not return anything, modify matrix in-place instead.
        """
        pass
''',
  hints=["A 90° rotation can be built from two simpler flips you can each do in place.",
         "Try: transpose the matrix (swap `matrix[i][j]` with `matrix[j][i]`), then reverse each row. Check it on a 3×3 by hand!",
         "Transpose: for `i` in range(n), for `j` in range(i + 1, n), swap `matrix[i][j], matrix[j][i]`. Then `for row in matrix: row.reverse()`."],
  solution=r'''class Solution:
    def rotate(self, matrix: List[List[int]]) -> None:
        n = len(matrix)
        for i in range(n):
            for j in range(i + 1, n):
                matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
        for row in matrix:
            row.reverse()
''',
  complexity="O(n²) time, O(1) space",
  driver='''def drive(args):
    matrix = args[0]
    Solution().rotate(matrix)
    return matrix
''',
  gen=lambda r: [[[[1]]], [[[1, 2], [3, 4]]]] + [[_matrix(r, n, n)] for n in [3, 5, 6, 10, 20]])


P(id=69, slug="spiral-matrix", title="Spiral Matrix", lc=54, difficulty="Medium", category="Math & Geometry",
  method="spiralOrder", params=["matrix"],
  description="""Given an `m x n` `matrix`, return all of its elements in **spiral order**: across the top row, down the right side, back along the bottom, up the left side, and then spiral inward.""",
  examples=[E([[1, 2, 3], [4, 5, 6], [7, 8, 9]], out=[1, 2, 3, 6, 9, 8, 7, 4, 5]),
            E([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]], out=[1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7])],
  constraints=["1 <= m, n <= 10", "-100 <= matrix[i][j] <= 100"],
  starter='''class Solution:
    def spiralOrder(self, matrix: List[List[int]]) -> List[int]:
        pass
''',
  hints=["Keep track of four boundaries — `top`, `bottom`, `left`, `right` — that shrink as you peel off each layer.",
         "Each loop: walk the top row left→right (then `top += 1`), the right column top→bottom (`right -= 1`), the bottom row right→left (`bottom -= 1`), the left column bottom→top (`left += 1`).",
         "Careful with single rows/columns: before walking the bottom row check `top <= bottom`, and before walking the left column check `left <= right`. Loop while `top <= bottom and left <= right`."],
  solution=r'''class Solution:
    def spiralOrder(self, matrix: List[List[int]]) -> List[int]:
        result = []
        top, bottom, left, right = 0, len(matrix) - 1, 0, len(matrix[0]) - 1
        while top <= bottom and left <= right:
            for c in range(left, right + 1):
                result.append(matrix[top][c])
            top += 1
            for r in range(top, bottom + 1):
                result.append(matrix[r][right])
            right -= 1
            if top <= bottom:
                for c in range(right, left - 1, -1):
                    result.append(matrix[bottom][c])
                bottom -= 1
            if left <= right:
                for r in range(bottom, top - 1, -1):
                    result.append(matrix[r][left])
                left += 1
        return result
''',
  complexity="O(m · n) time, O(1) extra space",
  gen=lambda r: [[[[1]]], [[[1, 2, 3]]], [[[1], [2], [3]]], [[[1, 2], [3, 4], [5, 6]]]]
  + [[_matrix(r, a, b)] for a, b in [(2, 5), (4, 4), (5, 3), (7, 9), (10, 10)]])


def _zero_gen(r):
    cases = [[[[0]]], [[[1, 0]]], [[[1], [0], [3]]], [[[1, 2, 3, 4], [5, 0, 7, 8], [0, 10, 11, 12], [13, 14, 15, 0]]]]
    for a, b in [(3, 3), (4, 5), (6, 6), (10, 8), (30, 30)]:
        m = _matrix(r, a, b, 1, 9)
        for _ in range(r.randint(1, 3)):
            m[r.randrange(a)][r.randrange(b)] = 0
        cases.append([m])
    return cases


P(id=70, slug="set-matrix-zeroes", title="Set Matrix Zeroes", lc=73, difficulty="Medium", category="Math & Geometry",
  method="setZeroes", params=["matrix"],
  description="""Given an `m x n` integer `matrix`, if an element is `0`, set its **entire row and column** to `0`. Do it **in place**.

*Follow-up:* the easy version uses O(m + n) extra space. Can you get it down to O(1)?""",
  examples=[E([[1, 1, 1], [1, 0, 1], [1, 1, 1]], out=[[1, 0, 1], [0, 0, 0], [1, 0, 1]]),
            E([[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]], out=[[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]])],
  constraints=["1 <= m, n <= 200", "-2^31 <= matrix[i][j] <= 2^31 - 1"],
  starter='''class Solution:
    def setZeroes(self, matrix: List[List[int]]) -> None:
        """
        Do not return anything, modify matrix in-place instead.
        """
        pass
''',
  hints=["If you zero things out as soon as you see a 0, the new zeros will trick you into wiping out extra rows and columns. Find all of them first.",
         "First pass: record which rows and which columns contain a zero (two sets). Second pass: zero every cell whose row or column was recorded.",
         "O(1)-space trick: use the first row and first column themselves as the 'recorded' markers, plus one extra flag for whether the first row itself needs zeroing. Fill the inner cells first, then the first column/row last."],
  solution=r'''class Solution:
    def setZeroes(self, matrix: List[List[int]]) -> None:
        rows = {r for r, row in enumerate(matrix) for v in row if v == 0}
        cols = {c for row in matrix for c, v in enumerate(row) if v == 0}
        for r in range(len(matrix)):
            for c in range(len(matrix[0])):
                if r in rows or c in cols:
                    matrix[r][c] = 0
''',
  complexity="O(m · n) time, O(m + n) space (O(1) with the marker trick)",
  driver='''def drive(args):
    matrix = args[0]
    Solution().setZeroes(matrix)
    return matrix
''',
  gen=_zero_gen)

# ======================================================== Bit Manipulation

P(id=71, slug="number-of-1-bits", title="Number of 1 Bits", lc=191, difficulty="Easy", category="Bit Manipulation",
  method="hammingWeight", params=["n"],
  description="""Given a positive integer `n`, return the number of `1` bits in its binary representation (also called its **Hamming weight**).""",
  examples=[E(11, out=3, why="11 in binary is 1011 — three 1s."), E(128, out=1, why="10000000"), E(2147483645, out=30)],
  constraints=["1 <= n <= 2^31 - 1"],
  starter='''class Solution:
    def hammingWeight(self, n: int) -> int:
        pass
''',
  hints=["You can look at the lowest bit with `n & 1`, and drop it with `n >> 1`.",
         "Loop until `n` becomes 0, adding `n & 1` to a counter and shifting right each time.",
         "Neat trick: `n & (n - 1)` clears the lowest set bit. Count how many times you can do `n &= n - 1` before `n` hits 0. (Python cheat: `bin(n).count('1')` — but try the bit way!)"],
  solution=r'''class Solution:
    def hammingWeight(self, n: int) -> int:
        count = 0
        while n:
            n &= n - 1
            count += 1
        return count
''',
  complexity="O(number of set bits) time, O(1) space",
  gen=lambda r: [[1], [2], [255], [2**31 - 1], [2**30]] + [[r.randint(1, 2**31 - 1)] for _ in range(5)])


P(id=72, slug="counting-bits", title="Counting Bits", lc=338, difficulty="Easy", category="Bit Manipulation",
  method="countBits", params=["n"],
  description="""Given an integer `n`, return an array `ans` of length `n + 1` where `ans[i]` is the **number of 1 bits** in the binary form of `i`, for every `i` from `0` to `n`.

*Follow-up:* can you do it in O(n) — one pass, without counting each number's bits from scratch?""",
  examples=[E(2, out=[0, 1, 1], why="0 → 0, 1 → 1, 2 → 10"), E(5, out=[0, 1, 1, 2, 1, 2])],
  constraints=["0 <= n <= 10^5"],
  starter='''class Solution:
    def countBits(self, n: int) -> List[int]:
        pass
''',
  hints=["Look for a relationship between `i` and a smaller number whose answer you already computed.",
         "`i >> 1` is `i` with its last bit removed, and it's smaller than `i`. The only difference is that last bit, `i & 1`.",
         "`ans = [0] * (n + 1)`; for `i` in `1..n`: `ans[i] = ans[i >> 1] + (i & 1)`. Return `ans`."],
  solution=r'''class Solution:
    def countBits(self, n: int) -> List[int]:
        ans = [0] * (n + 1)
        for i in range(1, n + 1):
            ans[i] = ans[i >> 1] + (i & 1)
        return ans
''',
  complexity="O(n) time, O(1) extra space",
  gen=lambda r: [[0], [1], [8], [16], [31], [100], [1000], [100000]])


P(id=73, slug="reverse-bits", title="Reverse Bits", lc=190, difficulty="Easy", category="Bit Manipulation",
  method="reverseBits", params=["n"],
  description="""Reverse the bits of a **32-bit unsigned integer** `n` and return the result as an integer.

For example, bit 0 (the lowest) becomes bit 31, bit 1 becomes bit 30, and so on. Always treat the number as exactly 32 bits, including leading zeros.""",
  examples=[E(43261596, out=964176192, why="00000010100101000001111010011100 → 00111001011110000010100101000000"),
            E(2147483644, out=1073741822)],
  constraints=["0 <= n <= 2^32 - 1 (passed as a regular Python int)"],
  starter='''class Solution:
    def reverseBits(self, n: int) -> int:
        pass
''',
  hints=["Build the answer one bit at a time: take bits off the low end of `n` and push them onto the low end of the result.",
         "Each step: shift the result left by 1 to make room, then OR in `n & 1`. Then shift `n` right by 1.",
         "`result = 0`; repeat exactly 32 times: `result = (result << 1) | (n & 1)`; `n >>= 1`. Return `result`. (Exactly 32 iterations matters — leading zeros count!)"],
  solution=r'''class Solution:
    def reverseBits(self, n: int) -> int:
        result = 0
        for _ in range(32):
            result = (result << 1) | (n & 1)
            n >>= 1
        return result
''',
  complexity="O(32) = O(1) time and space",
  gen=lambda r: [[0], [1], [2**32 - 1], [2**31], [4294967293]] + [[r.randint(0, 2**32 - 1)] for _ in range(5)])


def _missing_gen(r):
    cases = [[[0]], [[1]], [[1, 2]], [[2, 0]]]
    for n in [5, 10, 50, 1000, 10000]:
        nums = list(range(n + 1))
        nums.pop(r.randrange(n + 1))
        r.shuffle(nums)
        cases.append([nums])
    return cases


P(id=74, slug="missing-number", title="Missing Number", lc=268, difficulty="Easy", category="Bit Manipulation",
  method="missingNumber", params=["nums"],
  description="""You're given an array `nums` containing `n` **distinct** numbers taken from the range `[0, n]`. Exactly one number in that range is missing — return it.

*Follow-up:* can you do it with O(1) extra space and O(n) time?""",
  examples=[E([3, 0, 1], out=2, why="n = 3, so the range is 0..3, and 2 is missing."), E([0, 1], out=2), E([9, 6, 4, 2, 3, 5, 7, 0, 1], out=8)],
  constraints=["n == nums.length", "1 <= n <= 10^4", "All numbers are unique and in [0, n]."],
  starter='''class Solution:
    def missingNumber(self, nums: List[int]) -> int:
        pass
''',
  hints=["You know exactly which numbers *should* be there: 0, 1, …, n.",
         "Math way: the sum of 0..n is `n * (n + 1) // 2`. Bit way: `x ^ x == 0`, so XOR-ing every index with every value cancels out all the pairs.",
         "`return n * (n + 1) // 2 - sum(nums)` — or start `res = n` and do `res ^= i ^ nums[i]` for every `i`; what's left is the missing number."],
  solution=r'''class Solution:
    def missingNumber(self, nums: List[int]) -> int:
        res = len(nums)
        for i, x in enumerate(nums):
            res ^= i ^ x
        return res
''',
  complexity="O(n) time, O(1) space",
  gen=_missing_gen)


P(id=75, slug="sum-of-two-integers", title="Sum of Two Integers", lc=371, difficulty="Medium", category="Bit Manipulation",
  method="getSum", params=["a", "b"],
  description="""Given two integers `a` and `b`, return their sum **without using the `+` or `-` operators**.

(The runner can't stop you from using `+`… but the whole point is the bit trick. 😉 Heads up: Python ints have unlimited size, so negative numbers need a 32-bit mask.)""",
  examples=[E(1, 2, out=3), E(2, 3, out=5)],
  constraints=["-1000 <= a, b <= 1000"],
  starter='''class Solution:
    def getSum(self, a: int, b: int) -> int:
        pass
''',
  hints=["When you add in binary, each column produces a 'sum bit' and a 'carry bit'. Which bitwise operators compute those?",
         "`a ^ b` adds without carrying. `(a & b) << 1` is the carry. Keep adding the carry back in until there is none.",
         "Python needs a 32-bit mask: `mask = 0xFFFFFFFF`. Loop while `b`: `a, b = (a ^ b) & mask, ((a & b) << 1) & mask`. At the end, if `a > 0x7FFFFFFF` it's negative: return `~(a ^ mask)`; otherwise return `a`."],
  solution=r'''class Solution:
    def getSum(self, a: int, b: int) -> int:
        mask = 0xFFFFFFFF
        while b:
            a, b = (a ^ b) & mask, ((a & b) << 1) & mask
        return a if a <= 0x7FFFFFFF else ~(a ^ mask)
''',
  complexity="O(32) = O(1) time and space",
  gen=lambda r: [[0, 0], [-1, 1], [-5, -7], [1000, -1000], [-1000, 999]] + [[r.randint(-1000, 1000), r.randint(-1000, 1000)] for _ in range(5)])
