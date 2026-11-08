"""Blind 75, part 1: Arrays & Hashing → Linked List (problems 1–24)."""
from common import E, LIST_DEF, P, rand_ints, rand_str

# ======================================================== Arrays & Hashing


def _two_sum_gen(r):
    cases = []
    for n in [2, 3, 5, 8, 12, 20, 50, 400, 3000]:
        while True:
            nums = r.sample(range(-10**6, 10**6), n)
            i, j = r.sample(range(n), 2)
            target = nums[i] + nums[j]
            s = set(nums)
            pairs = sum(1 for x in nums if target - x in s and target - x != x)
            if pairs == 2:
                cases.append([nums, target])
                break
    cases.append([[5, 5, 1, 2], 10])
    cases.append([[-3, 4, 3, 90], 0])
    return cases


P(id=1, slug="two-sum", title="Two Sum", lc=1, difficulty="Easy", category="Arrays & Hashing",
  method="twoSum", params=["nums", "target"], compare="unordered",
  description="""Given an array of integers `nums` and an integer `target`, return the **indices** of the two numbers that add up to `target`.

Every input has exactly one valid answer, and you can't use the same element twice. You can return the two indices in any order.""",
  examples=[E([2, 7, 11, 15], 9, out=[0, 1], why="nums[0] + nums[1] == 9, so we return [0, 1]."),
            E([3, 2, 4], 6, out=[1, 2]), E([3, 3], 6, out=[0, 1])],
  constraints=["2 <= nums.length <= 10^4", "-10^9 <= nums[i], target <= 10^9", "Exactly one valid answer exists."],
  starter='''class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        pass
''',
  hints=["For each number `x`, what *other* number would you need to complete the pair? Is there a fast way to check whether you've already seen it?",
         "A hash map from value → index lets you look up the 'complement' (`target - x`) in O(1) time.",
         "Loop once with `enumerate`. If `target - x` is already in your map, return `[map[target - x], i]`. Otherwise store `map[x] = i` and keep going."],
  solution=r'''class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen = {}  # value -> index
        for i, x in enumerate(nums):
            if target - x in seen:
                return [seen[target - x], i]
            seen[x] = i
''',
  complexity="O(n) time, O(n) space",
  gen=_two_sum_gen)


def _dup_gen(r):
    cases = []
    for n in [1, 2, 2, 5, 10, 30, 100, 5000]:
        nums = r.sample(range(-10**9, 10**9), n)
        if n > 1 and r.random() < 0.5:
            nums[r.randrange(n)] = nums[r.randrange(n)]
        cases.append([nums])
    big = list(range(20000))
    cases.append([big])
    cases.append([big[:-1] + [0]])
    return cases


P(id=2, slug="contains-duplicate", title="Contains Duplicate", lc=217, difficulty="Easy", category="Arrays & Hashing",
  method="containsDuplicate", params=["nums"],
  description="""Given an integer array `nums`, return `True` if **any value appears at least twice**, and `False` if every element is distinct.""",
  examples=[E([1, 2, 3, 1], out=True, why="The value 1 shows up at index 0 and index 3."),
            E([1, 2, 3, 4], out=False), E([1, 1, 1, 3, 3, 4, 3, 2, 4, 2], out=True)],
  constraints=["1 <= nums.length <= 10^5", "-10^9 <= nums[i] <= 10^9"],
  starter='''class Solution:
    def containsDuplicate(self, nums: List[int]) -> bool:
        pass
''',
  hints=["If the array were sorted, where would two equal values end up relative to each other?",
         "A `set` remembers everything you've seen, with O(1) membership checks.",
         "Loop over `nums`: if `x` is already in your set, return `True`; otherwise add it. If the loop finishes, return `False`. (One-liner: `len(set(nums)) < len(nums)`.)"],
  solution=r'''class Solution:
    def containsDuplicate(self, nums: List[int]) -> bool:
        seen = set()
        for x in nums:
            if x in seen:
                return True
            seen.add(x)
        return False
''',
  complexity="O(n) time, O(n) space",
  gen=_dup_gen)


def _anagram_gen(r):
    cases = []
    for n in [1, 2, 3, 6, 10, 25, 500, 20000]:
        s = rand_str(r, n, "abcdef" if n < 30 else "abcdefghijklmnopqrstuvwxyz")
        t = list(s)
        r.shuffle(t)
        if r.random() < 0.45:
            k = r.randrange(n)
            t[k] = "z" if t[k] != "z" else "y"
        cases.append([s, "".join(t)])
    cases.append(["ab", "a"])
    cases.append(["aacc", "ccac"])
    return cases


P(id=3, slug="valid-anagram", title="Valid Anagram", lc=242, difficulty="Easy", category="Arrays & Hashing",
  method="isAnagram", params=["s", "t"],
  description="""Given two strings `s` and `t`, return `True` if `t` is an **anagram** of `s`, and `False` otherwise.

An anagram uses exactly the same letters as the original, the same number of times, just rearranged.""",
  examples=[E("anagram", "nagaram", out=True), E("rat", "car", out=False)],
  constraints=["1 <= s.length, t.length <= 5 * 10^4", "s and t consist of lowercase English letters."],
  starter='''class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        pass
''',
  hints=["Two words are anagrams exactly when every letter appears the same number of times in both.",
         "Count characters with a dictionary (or `collections.Counter`), or compare the sorted strings.",
         "Quick exit if `len(s) != len(t)`. Then build letter counts for both strings and check they're equal: `Counter(s) == Counter(t)`."],
  solution=r'''class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False
        count = {}
        for a, b in zip(s, t):
            count[a] = count.get(a, 0) + 1
            count[b] = count.get(b, 0) - 1
        return all(v == 0 for v in count.values())
''',
  complexity="O(n) time, O(1) space (26 letters)",
  gen=_anagram_gen)


def _group_gen(r):
    cases = []
    for groups in [1, 2, 4, 6, 10, 40]:
        words = set()
        for _ in range(groups):
            base = rand_str(r, r.randint(1, 6), "abcdeft")
            for _ in range(r.randint(1, 4)):
                w = list(base)
                r.shuffle(w)
                words.add("".join(w))
        lst = list(words)
        r.shuffle(lst)
        cases.append([lst])
    cases.append([["", "", "b"]])
    return cases


P(id=4, slug="group-anagrams", title="Group Anagrams", lc=49, difficulty="Medium", category="Arrays & Hashing",
  method="groupAnagrams", params=["strs"], compare="nested_unordered",
  description="""Given an array of strings `strs`, group the **anagrams** together. You can return the groups in any order, and the words inside each group in any order.

Two strings are anagrams if one is a rearrangement of the other's letters.""",
  examples=[E(["eat", "tea", "tan", "ate", "nat", "bat"], out=[["bat"], ["nat", "tan"], ["ate", "eat", "tea"]]),
            E([""], out=[[""]]), E(["a"], out=[["a"]])],
  constraints=["1 <= strs.length <= 10^4", "0 <= strs[i].length <= 100", "strs[i] consists of lowercase English letters."],
  starter='''class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        pass
''',
  hints=["What could you compute from a word that is *identical* for all of its anagrams?",
         "Use that 'signature' as a dictionary key — either the sorted word, or a tuple of 26 letter counts.",
         "Make `groups = defaultdict(list)`. For each word, `groups[tuple(sorted(word))].append(word)`. Return `list(groups.values())`."],
  solution=r'''class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        groups = defaultdict(list)
        for word in strs:
            counts = [0] * 26
            for ch in word:
                counts[ord(ch) - ord("a")] += 1
            groups[tuple(counts)].append(word)
        return list(groups.values())
''',
  complexity="O(n · k) time where k is the max word length, O(n · k) space",
  gen=_group_gen)


def _topk_gen(r):
    cases = []
    for distinct, k in [(1, 1), (3, 1), (4, 2), (6, 3), (10, 4), (30, 5), (200, 10)]:
        vals = r.sample(range(-1000, 1000), distinct)
        freqs = sorted(r.sample(range(1, distinct * 3 + 5), distinct), reverse=True)
        nums = []
        for v, f in zip(vals, freqs):
            nums += [v] * f
        r.shuffle(nums)
        cases.append([nums, k])
    return cases


P(id=5, slug="top-k-frequent-elements", title="Top K Frequent Elements", lc=347, difficulty="Medium", category="Arrays & Hashing",
  method="topKFrequent", params=["nums", "k"], compare="unordered",
  description="""Given an integer array `nums` and an integer `k`, return the `k` **most frequent** elements. You may return them in any order.

The answer is guaranteed to be unique.

*Follow-up:* can you beat O(n log n)?""",
  examples=[E([1, 1, 1, 2, 2, 3], 2, out=[1, 2]), E([1], 1, out=[1])],
  constraints=["1 <= nums.length <= 10^5", "k is in the range [1, number of distinct elements]", "The answer is unique."],
  starter='''class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        pass
''',
  hints=["Step one: figure out how many times each number appears.",
         "Once you have counts, you want the k biggest. Sorting works; a heap does it in O(n log k); 'bucket sort' by frequency does it in O(n).",
         "Bucket sort: `buckets[f]` = list of numbers that appear exactly `f` times (f goes up to `len(nums)`). Walk the buckets from the highest f downward, collecting numbers until you have k."],
  solution=r'''class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        count = Counter(nums)
        buckets = [[] for _ in range(len(nums) + 1)]
        for num, freq in count.items():
            buckets[freq].append(num)
        result = []
        for freq in range(len(buckets) - 1, 0, -1):
            for num in buckets[freq]:
                result.append(num)
                if len(result) == k:
                    return result
''',
  complexity="O(n) time, O(n) space",
  gen=_topk_gen)


def _codec_gen(r):
    alphabet = "ab#:,;|/\\ 0123456789\"'"
    cases = []
    for n in [0, 1, 2, 3, 5, 10, 40]:
        cases.append([[rand_str(r, r.randint(0, 12), alphabet) for _ in range(n)]])
    cases.append([["", "", ""]])
    cases.append([["3#abc", "12#", "#"]])
    return cases


P(id=6, slug="encode-and-decode-strings", title="Encode and Decode Strings", lc=271, difficulty="Medium", category="Arrays & Hashing",
  params=["strs"],
  description="""Design an algorithm that **encodes** a list of strings into a single string, and **decodes** that single string back into the original list.

Implement `encode(strs)` and `decode(s)` so that `decode(encode(strs)) == strs` for *any* list of strings. Watch out: the strings can contain any characters at all, including whatever delimiter you might be tempted to use!

The test runner calls `encode`, checks it returns a `str`, then passes that string to `decode` and compares the result with the original list.""",
  examples=[E(["neet", "code", "love", "you"], out=["neet", "code", "love", "you"]),
            E(["we", "say", ":", "yes"], out=["we", "say", ":", "yes"]),
            E([""], out=[""])],
  constraints=["0 <= strs.length < 200", "0 <= strs[i].length < 200", "strs[i] can contain any of the 256 ASCII characters."],
  starter='''class Solution:
    def encode(self, strs: List[str]) -> str:
        pass

    def decode(self, s: str) -> List[str]:
        pass
''',
  hints=["Joining with a separator like `,` breaks as soon as a string contains a `,`. How can the decoder know where each string ends *without* looking at its contents?",
         "Store each string's length in front of it, followed by a marker character — e.g. `\"4#neet\"`.",
         "encode: `''.join(f'{len(s)}#{s}' for s in strs)`. decode: keep an index `i`; scan forward to the next `#` to read the length L, take the next L characters as one string, jump `i` past them, and repeat until the end."],
  solution=r'''class Solution:
    def encode(self, strs: List[str]) -> str:
        return "".join(f"{len(s)}#{s}" for s in strs)

    def decode(self, s: str) -> List[str]:
        result, i = [], 0
        while i < len(s):
            j = s.index("#", i)
            length = int(s[i:j])
            result.append(s[j + 1 : j + 1 + length])
            i = j + 1 + length
        return result
''',
  complexity="O(total characters) time and space",
  driver='''def drive(args):
    sol = Solution()
    encoded = sol.encode(args[0])
    if not isinstance(encoded, str):
        raise TypeError(f"encode() should return a str, but returned {type(encoded).__name__}")
    return sol.decode(encoded)
''',
  gen=_codec_gen)


def _product_gen(r):
    cases = []
    for n in [2, 3, 5, 8, 15, 40]:
        cases.append([rand_ints(r, n, -5, 5)])
    cases.append([[0, 0, 2, 3]])
    cases.append([[1, 2, 0, 4]])
    cases.append([rand_ints(r, 5000, 1, 2)[:30] + [1] * 4970])
    return cases


P(id=7, slug="product-of-array-except-self", title="Product of Array Except Self", lc=238, difficulty="Medium", category="Arrays & Hashing",
  method="productExceptSelf", params=["nums"],
  description="""Given an integer array `nums`, return an array `answer` where `answer[i]` is the product of **every element of `nums` except `nums[i]`**.

Your algorithm must run in O(n) time and **must not use division**.

*Follow-up:* can you do it with O(1) extra space (the output array doesn't count)?""",
  examples=[E([1, 2, 3, 4], out=[24, 12, 8, 6]), E([-1, 1, 0, -3, 3], out=[0, 0, 9, 0, 0])],
  constraints=["2 <= nums.length <= 10^5", "-30 <= nums[i] <= 30", "Every prefix/suffix product fits in a 32-bit integer."],
  starter='''class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        pass
''',
  hints=["`answer[i]` = (product of everything to the *left* of i) × (product of everything to the *right* of i).",
         "You can compute all the left-products in one pass, and all the right-products in another pass.",
         "Fill `answer[i]` with the running prefix product going left→right. Then sweep right→left with a running `suffix` variable, multiplying `answer[i] *= suffix` and then `suffix *= nums[i]`."],
  solution=r'''class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        n = len(nums)
        answer = [1] * n
        prefix = 1
        for i in range(n):
            answer[i] = prefix
            prefix *= nums[i]
        suffix = 1
        for i in range(n - 1, -1, -1):
            answer[i] *= suffix
            suffix *= nums[i]
        return answer
''',
  complexity="O(n) time, O(1) extra space",
  gen=_product_gen)


def _consec_gen(r):
    cases = [[[]], [[5]], [[1, 2, 0, 1]], [[9, 1, 4, 7, 3, -1, 0, 5, 8, -1, 6]]]
    for n in [10, 50, 300]:
        cases.append([rand_ints(r, n, -n, n)])
    big = list(range(0, 30000, 1)) + list(range(50000, 60000, 2))
    r.shuffle(big)
    cases.append([big])
    return cases


P(id=8, slug="longest-consecutive-sequence", title="Longest Consecutive Sequence", lc=128, difficulty="Medium", category="Arrays & Hashing",
  method="longestConsecutive", params=["nums"],
  description="""Given an **unsorted** array of integers `nums`, return the length of the longest run of consecutive values (like `4, 5, 6, 7`). The values don't need to be next to each other in the array.

Aim for an O(n) solution.""",
  examples=[E([100, 4, 200, 1, 3, 2], out=4, why="The longest consecutive run is [1, 2, 3, 4], so the answer is 4."),
            E([0, 3, 7, 2, 5, 8, 4, 6, 0, 1], out=9), E([1, 0, 1, 2], out=3)],
  constraints=["0 <= nums.length <= 10^5", "-10^9 <= nums[i] <= 10^9"],
  starter='''class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        pass
''',
  hints=["Sorting gives O(n log n). To get O(n), put everything in a `set` so you can ask \"is x+1 here?\" instantly.",
         "Only start counting from numbers that *begin* a run — that is, `x` where `x - 1` is not in the set.",
         "For each `x` in the set with `x - 1` not in the set, count upward `x+1, x+2, …` while they're in the set. Track the max length. Each number is visited at most twice overall."],
  solution=r'''class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        values = set(nums)
        best = 0
        for x in values:
            if x - 1 not in values:
                length = 1
                while x + length in values:
                    length += 1
                best = max(best, length)
        return best
''',
  complexity="O(n) time, O(n) space",
  gen=_consec_gen)

# ============================================================ Two Pointers


def _pal_gen(r):
    cases = [[""], ["a."], ["0P"], [".,"], ["ab_a"], ["Was it a car or a cat I saw?"], ["No 'x' in Nixon"]]
    for n in [5, 12, 40, 2000]:
        half = rand_str(r, n, "abcABC12 ,.:!")
        s = half + half[::-1]
        if r.random() < 0.5:
            s = s[: n // 2] + "q" + s[n // 2 :]
        cases.append([s])
    return cases


P(id=9, slug="valid-palindrome", title="Valid Palindrome", lc=125, difficulty="Easy", category="Two Pointers",
  method="isPalindrome", params=["s"],
  description="""A phrase is a **palindrome** if, after converting all uppercase letters to lowercase and removing every non-alphanumeric character, it reads the same forward and backward. (Letters and digits count as alphanumeric.)

Given a string `s`, return `True` if it's a palindrome, or `False` otherwise.""",
  examples=[E("A man, a plan, a canal: Panama", out=True, why="Cleaned up, it's \"amanaplanacanalpanama\" — a palindrome!"),
            E("race a car", out=False), E(" ", out=True, why="After cleaning, s is an empty string, which reads the same both ways.")],
  constraints=["1 <= s.length <= 2 * 10^5", "s consists of printable ASCII characters."],
  starter='''class Solution:
    def isPalindrome(self, s: str) -> bool:
        pass
''',
  hints=["The simple way: build a cleaned, lowercased string and compare it to its reverse. Can you do it without the extra string?",
         "Use two pointers, one at each end, walking toward each other. `str.isalnum()` tells you which characters to skip.",
         "While `l < r`: move `l` right past non-alphanumerics, move `r` left past non-alphanumerics, then compare `s[l].lower()` with `s[r].lower()`. Mismatch → `False`. Otherwise step both inward."],
  solution=r'''class Solution:
    def isPalindrome(self, s: str) -> bool:
        l, r = 0, len(s) - 1
        while l < r:
            while l < r and not s[l].isalnum():
                l += 1
            while l < r and not s[r].isalnum():
                r -= 1
            if s[l].lower() != s[r].lower():
                return False
            l, r = l + 1, r - 1
        return True
''',
  complexity="O(n) time, O(1) space",
  gen=_pal_gen)


def _3sum_gen(r):
    cases = [[[0, 0, 0, 0]], [[-2, 0, 1, 1, 2]], [[1, 2, -2, -1]], [[-1, 0, 1, 0]]]
    for n in [5, 8, 15, 30, 80, 400]:
        cases.append([rand_ints(r, n, -12, 12) if n < 100 else rand_ints(r, n, -10**4, 10**4)])
    return cases


P(id=10, slug="3sum", title="3Sum", lc=15, difficulty="Medium", category="Two Pointers",
  method="threeSum", params=["nums"], compare="nested_unordered",
  description="""Given an integer array `nums`, return **all unique triplets** `[nums[i], nums[j], nums[k]]` where `i`, `j`, `k` are different indices and `nums[i] + nums[j] + nums[k] == 0`.

The answer must not contain duplicate triplets. Order of triplets (and of numbers within a triplet) doesn't matter.""",
  examples=[E([-1, 0, 1, 2, -1, -4], out=[[-1, -1, 2], [-1, 0, 1]]),
            E([0, 1, 1], out=[], why="No three numbers add up to 0."), E([0, 0, 0], out=[[0, 0, 0]])],
  constraints=["3 <= nums.length <= 3000", "-10^5 <= nums[i] <= 10^5"],
  starter='''class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        pass
''',
  hints=["Sorting first makes both 'searching for a sum' and 'skipping duplicates' much easier.",
         "Fix the first number `nums[i]`, then the problem becomes Two Sum on the rest of a *sorted* array — which two pointers solve in O(n).",
         "Sort. For each `i` (skip if `nums[i] == nums[i-1]`), set `l = i+1, r = n-1`. If the sum is too small move `l` right, too big move `r` left; on a hit, record it, then move `l` right past any duplicates."],
  solution=r'''class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        nums.sort()
        result = []
        for i in range(len(nums) - 2):
            if i > 0 and nums[i] == nums[i - 1]:
                continue
            l, r = i + 1, len(nums) - 1
            while l < r:
                total = nums[i] + nums[l] + nums[r]
                if total < 0:
                    l += 1
                elif total > 0:
                    r -= 1
                else:
                    result.append([nums[i], nums[l], nums[r]])
                    l += 1
                    while l < r and nums[l] == nums[l - 1]:
                        l += 1
        return result
''',
  complexity="O(n²) time, O(1) extra space (besides sorting)",
  gen=_3sum_gen)


def _water_gen(r):
    cases = [[[4, 3, 2, 1, 4]], [[1, 2, 1]], [[2, 3, 4, 5, 18, 17, 6]]]
    for n in [3, 6, 10, 50, 5000]:
        cases.append([rand_ints(r, n, 0, 10**4)])
    return cases


P(id=11, slug="container-with-most-water", title="Container With Most Water", lc=11, difficulty="Medium", category="Two Pointers",
  method="maxArea", params=["height"],
  description="""You're given an array `height` of length `n`. Picture `n` vertical lines, where line `i` goes from `(i, 0)` up to `(i, height[i])`.

Pick two lines that, together with the x-axis, form a container. Return the **maximum amount of water** a container can hold. (The container can't be tilted, so the water level is set by the shorter line.)""",
  examples=[E([1, 8, 6, 2, 5, 4, 8, 3, 7], out=49, why="Lines at index 1 (height 8) and index 8 (height 7): width 7 × height 7 = 49."),
            E([1, 1], out=1)],
  constraints=["2 <= n <= 10^5", "0 <= height[i] <= 10^4"],
  starter='''class Solution:
    def maxArea(self, height: List[int]) -> int:
        pass
''',
  hints=["Area = `(r - l) * min(height[l], height[r])`. Checking every pair is O(n²) — can you rule pairs out?",
         "Start with the widest container (both ends). Moving the *taller* line inward can never help — the width shrinks and the height is still capped by the shorter line.",
         "Two pointers `l = 0`, `r = n-1`. Record the area, then move whichever pointer points to the shorter line inward. Repeat while `l < r`, keeping the max."],
  solution=r'''class Solution:
    def maxArea(self, height: List[int]) -> int:
        l, r = 0, len(height) - 1
        best = 0
        while l < r:
            best = max(best, (r - l) * min(height[l], height[r]))
            if height[l] < height[r]:
                l += 1
            else:
                r -= 1
        return best
''',
  complexity="O(n) time, O(1) space",
  gen=_water_gen)

# ========================================================== Sliding Window


def _stock_gen(r):
    cases = [[[1]], [[2, 4, 1]], [[3, 2, 6, 5, 0, 3]], [[1, 2]]]
    for n in [5, 10, 40, 5000]:
        cases.append([rand_ints(r, n, 0, 10**4)])
    cases.append([list(range(5000, 0, -1))])
    return cases


P(id=12, slug="best-time-to-buy-and-sell-stock", title="Best Time to Buy and Sell Stock", lc=121, difficulty="Easy", category="Sliding Window",
  method="maxProfit", params=["prices"],
  description="""You're given an array `prices` where `prices[i]` is a stock's price on day `i`.

You want to buy on one day and sell on a **later** day. Return the maximum profit you can make. If no profit is possible, return `0`.""",
  examples=[E([7, 1, 5, 3, 6, 4], out=5, why="Buy on day 1 (price 1) and sell on day 4 (price 6): profit 6 − 1 = 5."),
            E([7, 6, 4, 3, 1], out=0, why="Prices only go down, so the best move is not to trade.")],
  constraints=["1 <= prices.length <= 10^5", "0 <= prices[i] <= 10^4"],
  starter='''class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        pass
''',
  hints=["If you sell on day i, which buy day gives you the best profit?",
         "As you walk through the days, keep track of the cheapest price seen *so far*.",
         "One pass: `lowest = min(lowest, price)` and `best = max(best, price - lowest)`. Return `best`."],
  solution=r'''class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        lowest = float("inf")
        best = 0
        for price in prices:
            lowest = min(lowest, price)
            best = max(best, price - lowest)
        return best
''',
  complexity="O(n) time, O(1) space",
  gen=_stock_gen)


def _lswr_gen(r):
    cases = [["au"], ["dvdf"], ["abba"], [" "], ["tmmzuxt"]]
    for n in [5, 10, 30, 100, 20000]:
        cases.append([rand_str(r, n, "abcdefghij !?" if n < 100 else "abcdefghijklmnopqrstuvwxyzABCDEF0123456789")])
    return cases


P(id=13, slug="longest-substring-without-repeating-characters", title="Longest Substring Without Repeating Characters", lc=3,
  difficulty="Medium", category="Sliding Window", method="lengthOfLongestSubstring", params=["s"],
  description="""Given a string `s`, find the length of the **longest substring** that has no repeated characters.

A substring is a contiguous block of characters.""",
  examples=[E("abcabcbb", out=3, why="\"abc\" has length 3."), E("bbbbb", out=1),
            E("pwwkew", out=3, why="\"wke\" works. Note \"pwke\" is a subsequence, not a substring."),
            E("", out=0)],
  constraints=["0 <= s.length <= 5 * 10^4", "s consists of English letters, digits, symbols and spaces."],
  starter='''class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        pass
''',
  hints=["Think of a window `s[l:r+1]` that never contains a duplicate. As `r` moves right, when does `l` need to move?",
         "When the new character `s[r]` is already in the window, shrink from the left until it isn't. A set (or a dict of last-seen indices) tracks what's in the window.",
         "With a dict `last[ch] = index`: for each `r`, if `s[r]` was seen at index ≥ `l`, jump `l = last[s[r]] + 1`. Then `last[s[r]] = r` and `best = max(best, r - l + 1)`."],
  solution=r'''class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        last = {}
        l = best = 0
        for r, ch in enumerate(s):
            if ch in last and last[ch] >= l:
                l = last[ch] + 1
            last[ch] = r
            best = max(best, r - l + 1)
        return best
''',
  complexity="O(n) time, O(alphabet) space",
  gen=_lswr_gen)


def _crr_gen(r):
    cases = [["A", 0], ["AAAA", 0], ["ABCDE", 1], ["ABBB", 2], ["BAAA", 0]]
    for n in [6, 12, 30, 200, 20000]:
        cases.append([rand_str(r, n, "ABC" if n < 100 else "ABCDEFGH"), r.randint(0, max(1, n // 4))])
    return cases


P(id=14, slug="longest-repeating-character-replacement", title="Longest Repeating Character Replacement", lc=424,
  difficulty="Medium", category="Sliding Window", method="characterReplacement", params=["s", "k"],
  description="""You're given a string `s` of uppercase letters and an integer `k`. You may pick any character and change it to any other uppercase letter — at most `k` times total.

Return the length of the **longest substring containing only one repeated letter** you can get after making those changes.""",
  examples=[E("ABAB", 2, out=4, why="Change both A's to B (or both B's to A) to get \"BBBB\"."),
            E("AABABBA", 1, out=4, why="Change the middle A to B: \"AABBBBA\" contains \"BBBB\".")],
  constraints=["1 <= s.length <= 10^5", "s consists of uppercase English letters.", "0 <= k <= s.length"],
  starter='''class Solution:
    def characterReplacement(self, s: str, k: int) -> int:
        pass
''',
  hints=["For a given window, how many characters would you need to change so they all match? (Hint: keep the most common letter and change the rest.)",
         "A window is valid when `window_length - count_of_most_frequent_letter <= k`. Grow the window to the right; shrink from the left when it becomes invalid.",
         "Keep `count` of letters in the window and `maxf` = highest count seen. For each `r`: add `s[r]`, update `maxf`; while `(r - l + 1) - maxf > k`, remove `s[l]` and `l += 1`. Track the best window size. (It's fine that `maxf` never decreases!)"],
  solution=r'''class Solution:
    def characterReplacement(self, s: str, k: int) -> int:
        count = {}
        l = maxf = best = 0
        for r, ch in enumerate(s):
            count[ch] = count.get(ch, 0) + 1
            maxf = max(maxf, count[ch])
            while (r - l + 1) - maxf > k:
                count[s[l]] -= 1
                l += 1
            best = max(best, r - l + 1)
        return best
''',
  complexity="O(n) time, O(26) space",
  gen=_crr_gen)


def _minwin_gen(r):
    cases = [["ab", "b"], ["bba", "ab"], ["aa", "aa"], ["abc", "cba"], ["acbbaca", "aba"]]
    for n, m in [(5, 2), (10, 3), (20, 4), (60, 5), (300, 8), (20000, 15)]:
        cases.append([rand_str(r, n, "ABCDEFxyz"), rand_str(r, m, "ABCDEF")])
    return cases


P(id=15, slug="minimum-window-substring", title="Minimum Window Substring", lc=76, difficulty="Hard", category="Sliding Window",
  method="minWindow", params=["s", "t"], compare="min_window",
  description="""Given strings `s` and `t`, return the **shortest substring of `s`** that contains every character of `t` (including duplicates — if `t` has two `a`s, the window needs at least two `a`s).

If there's no such window, return the empty string `""`. If several windows tie for shortest, any one is accepted.""",
  examples=[E("ADOBECODEBANC", "ABC", out="BANC", why="\"BANC\" has an A, a B and a C, and nothing shorter does."),
            E("a", "a", out="a"), E("a", "aa", out="", why="t needs two a's but s only has one.")],
  constraints=["1 <= s.length, t.length <= 10^5", "s and t consist of uppercase and lowercase English letters."],
  starter='''class Solution:
    def minWindow(self, s: str, t: str) -> str:
        pass
''',
  hints=["Expand a window to the right until it contains everything in `t`, then try shrinking it from the left as much as possible while it stays valid.",
         "Keep `need = Counter(t)` and a `window` counter. Track how many distinct characters currently meet their required count (`have` vs `required = len(need)`) so validity is an O(1) check.",
         "For each `r`: add `s[r]`; if its count just reached `need[s[r]]`, `have += 1`. While `have == required`: record the window if it's the smallest yet, then remove `s[l]` (if its count drops below `need`, `have -= 1`) and `l += 1`."],
  solution=r'''class Solution:
    def minWindow(self, s: str, t: str) -> str:
        need = Counter(t)
        window = {}
        have, required = 0, len(need)
        best_len, best_l = float("inf"), 0
        l = 0
        for r, ch in enumerate(s):
            window[ch] = window.get(ch, 0) + 1
            if ch in need and window[ch] == need[ch]:
                have += 1
            while have == required:
                if r - l + 1 < best_len:
                    best_len, best_l = r - l + 1, l
                window[s[l]] -= 1
                if s[l] in need and window[s[l]] < need[s[l]]:
                    have -= 1
                l += 1
        return "" if best_len == float("inf") else s[best_l : best_l + best_len]
''',
  complexity="O(|s| + |t|) time, O(alphabet) space",
  gen=_minwin_gen)

# =================================================================== Stack


def _paren_gen(r):
    cases = [["["], ["]"], ["(("], ["){"], ["{[]}"], ["(([]){})"], ["(){}}{"]]
    for n in [4, 8, 16, 40, 10000]:
        stack, s = [], []
        pairs = {"(": ")", "[": "]", "{": "}"}
        for _ in range(n // 2):
            if stack and r.random() < 0.5:
                s.append(pairs[stack.pop()])
            else:
                o = r.choice("([{")
                stack.append(o)
                s.append(o)
        while stack:
            s.append(pairs[stack.pop()])
        if r.random() < 0.5:
            i = r.randrange(len(s))
            s[i] = r.choice("()[]{}")
        cases.append(["".join(s)])
    return cases


P(id=16, slug="valid-parentheses", title="Valid Parentheses", lc=20, difficulty="Easy", category="Stack",
  method="isValid", params=["s"],
  description="""Given a string `s` made of just the characters `(`, `)`, `{`, `}`, `[` and `]`, decide whether it's **valid**:

1. Every opening bracket is closed by the same type of bracket.
2. Brackets close in the correct order.
3. Every closing bracket has a matching opening bracket.""",
  examples=[E("()", out=True), E("()[]{}", out=True), E("(]", out=False), E("([])", out=True), E("([)]", out=False)],
  constraints=["1 <= s.length <= 10^4", "s consists only of the characters '()[]{}'."],
  starter='''class Solution:
    def isValid(self, s: str) -> bool:
        pass
''',
  hints=["When you see a closing bracket, which opening bracket does it need to match?",
         "The most recent *unmatched* opening bracket — last in, first out. That's a stack!",
         "Push opening brackets. On a closing bracket, if the stack is empty or its top isn't the matching opener, return `False`; otherwise pop. At the end, the string is valid only if the stack is empty."],
  solution=r'''class Solution:
    def isValid(self, s: str) -> bool:
        match = {")": "(", "]": "[", "}": "{"}
        stack = []
        for ch in s:
            if ch in match:
                if not stack or stack[-1] != match[ch]:
                    return False
                stack.pop()
            else:
                stack.append(ch)
        return not stack
''',
  complexity="O(n) time, O(n) space",
  gen=_paren_gen)

# =========================================================== Binary Search


def _rotated(r, n):
    vals = sorted(r.sample(range(-5000, 5000), n))
    k = r.randrange(n)
    return vals[k:] + vals[:k]


def _findmin_gen(r):
    cases = [[[1]], [[2, 1]], [[1, 2]], [[5, 1, 2, 3, 4]], [[2, 3, 4, 5, 1]]]
    for n in [3, 7, 20, 100, 5000]:
        cases.append([_rotated(r, n)])
    return cases


P(id=17, slug="find-minimum-in-rotated-sorted-array", title="Find Minimum in Rotated Sorted Array", lc=153,
  difficulty="Medium", category="Binary Search", method="findMin", params=["nums"],
  description="""An array of **unique** integers was sorted in ascending order and then **rotated** some number of times. For example, `[0,1,2,4,5,6,7]` rotated 4 times becomes `[4,5,6,7,0,1,2]`.

Given the rotated array `nums`, return its minimum element. Your algorithm must run in **O(log n)** time.""",
  examples=[E([3, 4, 5, 1, 2], out=1, why="The original array was [1,2,3,4,5], rotated 3 times."),
            E([4, 5, 6, 7, 0, 1, 2], out=0), E([11, 13, 15, 17], out=11)],
  constraints=["1 <= n <= 5000", "-5000 <= nums[i] <= 5000", "All values are unique.", "nums is sorted and rotated 1 to n times."],
  starter='''class Solution:
    def findMin(self, nums: List[int]) -> int:
        pass
''',
  hints=["O(log n) means binary search. Compare the middle element to something that tells you which half the 'drop' is in.",
         "Compare `nums[mid]` with `nums[r]`. If `nums[mid] > nums[r]`, the minimum must be to the right of `mid`. Otherwise it's at `mid` or to its left.",
         "`l, r = 0, n-1`. While `l < r`: `mid = (l + r) // 2`; if `nums[mid] > nums[r]`: `l = mid + 1` else `r = mid`. Return `nums[l]`."],
  solution=r'''class Solution:
    def findMin(self, nums: List[int]) -> int:
        l, r = 0, len(nums) - 1
        while l < r:
            mid = (l + r) // 2
            if nums[mid] > nums[r]:
                l = mid + 1
            else:
                r = mid
        return nums[l]
''',
  complexity="O(log n) time, O(1) space",
  gen=_findmin_gen)


def _search_gen(r):
    cases = [[[1], 1], [[1, 3], 3], [[3, 1], 1], [[5, 1, 3], 5], [[4, 5, 6, 7, 8, 1, 2, 3], 8]]
    for n in [3, 7, 20, 100, 5000]:
        nums = _rotated(r, n)
        target = r.choice(nums) if r.random() < 0.7 else r.randint(-5000, 5000)
        cases.append([nums, target])
    return cases


P(id=18, slug="search-in-rotated-sorted-array", title="Search in Rotated Sorted Array", lc=33,
  difficulty="Medium", category="Binary Search", method="search", params=["nums", "target"],
  description="""An ascending array of **distinct** integers has been rotated at some unknown pivot (for example `[0,1,2,4,5,6,7]` might become `[4,5,6,7,0,1,2]`).

Given the rotated array `nums` and an integer `target`, return the index of `target`, or `-1` if it isn't there. You must write an **O(log n)** algorithm.""",
  examples=[E([4, 5, 6, 7, 0, 1, 2], 0, out=4), E([4, 5, 6, 7, 0, 1, 2], 3, out=-1), E([1], 0, out=-1)],
  constraints=["1 <= nums.length <= 5000", "-10^4 <= nums[i], target <= 10^4", "All values in nums are unique."],
  starter='''class Solution:
    def search(self, nums: List[int], target: int) -> int:
        pass
''',
  hints=["When you split a rotated array at `mid`, at least one of the two halves is perfectly sorted.",
         "Figure out which half is sorted (compare `nums[l]` with `nums[mid]`), then check whether `target` falls inside that sorted half's range.",
         "If `nums[l] <= nums[mid]` (left half sorted): if `nums[l] <= target < nums[mid]` search left (`r = mid - 1`), else search right. Otherwise the right half is sorted: if `nums[mid] < target <= nums[r]` go right, else go left."],
  solution=r'''class Solution:
    def search(self, nums: List[int], target: int) -> int:
        l, r = 0, len(nums) - 1
        while l <= r:
            mid = (l + r) // 2
            if nums[mid] == target:
                return mid
            if nums[l] <= nums[mid]:
                if nums[l] <= target < nums[mid]:
                    r = mid - 1
                else:
                    l = mid + 1
            else:
                if nums[mid] < target <= nums[r]:
                    l = mid + 1
                else:
                    r = mid - 1
        return -1
''',
  complexity="O(log n) time, O(1) space",
  gen=_search_gen)

# ============================================================= Linked List


def _rev_gen(r):
    return [[[1]], [[7, 7, 3]]] + [[rand_ints(r, n, -5000, 5000)] for n in [3, 6, 15, 100, 4000]]


P(id=19, slug="reverse-linked-list", title="Reverse Linked List", lc=206, difficulty="Easy", category="Linked List",
  method="reverseList", params=["head"],
  description="""Given the `head` of a singly linked list, reverse the list and return the **new head**.

(In the examples, linked lists are written as arrays — the test runner builds real `ListNode` chains for you.)""",
  examples=[E([1, 2, 3, 4, 5], out=[5, 4, 3, 2, 1]), E([1, 2], out=[2, 1]), E([], out=[])],
  constraints=["0 <= number of nodes <= 5000", "-5000 <= Node.val <= 5000"],
  starter=LIST_DEF + '''class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        pass
''',
  hints=["Walk the list once, flipping each node's `next` pointer to point backward. What do you need to remember so you don't lose the rest of the list?",
         "Keep two pointers: `prev` (starts as `None`) and `cur` (starts at `head`). Save `cur.next` before you overwrite it.",
         "Loop while `cur`: `nxt = cur.next; cur.next = prev; prev = cur; cur = nxt`. When the loop ends, `prev` is the new head."],
  solution=LIST_DEF + r'''class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        prev, cur = None, head
        while cur:
            nxt = cur.next
            cur.next = prev
            prev, cur = cur, nxt
        return prev
''',
  complexity="O(n) time, O(1) space",
  driver='''def drive(args):
    return list_to_arr(Solution().reverseList(build_list(args[0])))
''',
  gen=_rev_gen)


def _merge2_gen(r):
    cases = [[[1], []], [[5], [1, 2, 4]], [[1, 1, 1], [1, 1]]]
    for a, b in [(2, 3), (5, 5), (10, 1), (20, 30), (50, 50)]:
        cases.append([sorted(rand_ints(r, a, -100, 100)), sorted(rand_ints(r, b, -100, 100))])
    return cases


P(id=20, slug="merge-two-sorted-lists", title="Merge Two Sorted Lists", lc=21, difficulty="Easy", category="Linked List",
  method="mergeTwoLists", params=["list1", "list2"],
  description="""You're given the heads of two **sorted** linked lists, `list1` and `list2`.

Merge them into one sorted list by splicing together the nodes of the two lists, and return the head of the merged list.""",
  examples=[E([1, 2, 4], [1, 3, 4], out=[1, 1, 2, 3, 4, 4]), E([], [], out=[]), E([], [0], out=[0])],
  constraints=["0 <= number of nodes in each list <= 50", "-100 <= Node.val <= 100", "Both lists are sorted in non-decreasing order."],
  starter=LIST_DEF + '''class Solution:
    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
        pass
''',
  hints=["At each step, the next node of the merged list is whichever of the two current heads is smaller.",
         "A 'dummy' starting node saves you from special-casing the very first node.",
         "`dummy = tail = ListNode()`. While both lists remain, attach the smaller head to `tail.next`, advance that list and `tail`. Afterwards attach whichever list is left over. Return `dummy.next`."],
  solution=LIST_DEF + r'''class Solution:
    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
        dummy = tail = ListNode()
        while list1 and list2:
            if list1.val <= list2.val:
                tail.next, list1 = list1, list1.next
            else:
                tail.next, list2 = list2, list2.next
            tail = tail.next
        tail.next = list1 or list2
        return dummy.next
''',
  complexity="O(n + m) time, O(1) space",
  driver='''def drive(args):
    return list_to_arr(Solution().mergeTwoLists(build_list(args[0]), build_list(args[1])))
''',
  gen=_merge2_gen)


def _cycle_gen(r):
    cases = [[[], -1], [[1], 0], [[1, 2], 1], [[1, 2], -1]]
    for n in [3, 5, 10, 100, 5000]:
        cases.append([rand_ints(r, n, -10**5, 10**5), r.randrange(-1, n)])
    return cases


P(id=21, slug="linked-list-cycle", title="Linked List Cycle", lc=141, difficulty="Easy", category="Linked List",
  method="hasCycle", params=["head", "pos"],
  description="""Given `head`, the head of a linked list, determine whether the list contains a **cycle** — that is, some node can be reached again by repeatedly following `next`.

In the examples, `pos` is the index of the node the tail's `next` points back to (`-1` means no cycle). `pos` is only used to build the test list; it is **not** passed to your function.

*Follow-up:* can you solve it using O(1) memory?""",
  examples=[E([3, 2, 0, -4], 1, out=True, why="The tail connects back to the node at index 1."),
            E([1, 2], 0, out=True), E([1], -1, out=False)],
  constraints=["0 <= number of nodes <= 10^4", "-10^5 <= Node.val <= 10^5", "pos is -1 or a valid index."],
  starter=LIST_DEF + '''class Solution:
    def hasCycle(self, head: Optional[ListNode]) -> bool:
        pass
''',
  hints=["One idea: remember every node you've visited in a set (store the node objects themselves). Can you do it with O(1) memory?",
         "Floyd's tortoise and hare: move one pointer 1 step at a time and another 2 steps at a time. If there's a loop, the fast one eventually laps the slow one.",
         "`slow = fast = head`. While `fast and fast.next`: `slow = slow.next; fast = fast.next.next`; if `slow is fast` return `True`. If the loop exits, return `False`."],
  solution=LIST_DEF + r'''class Solution:
    def hasCycle(self, head: Optional[ListNode]) -> bool:
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            if slow is fast:
                return True
        return False
''',
  complexity="O(n) time, O(1) space",
  driver='''def drive(args):
    return Solution().hasCycle(build_cycle(args[0], args[1]))
''',
  gen=_cycle_gen)


def _reorder_gen(r):
    return [[[1]], [[1, 2]], [[1, 2, 3]]] + [[rand_ints(r, n, 1, 1000)] for n in [6, 7, 12, 25, 1000]]


P(id=22, slug="reorder-list", title="Reorder List", lc=143, difficulty="Medium", category="Linked List",
  method="reorderList", params=["head"],
  description="""You're given the head of a singly linked list: `L0 → L1 → … → Ln-1 → Ln`.

Reorder it **in place** to: `L0 → Ln → L1 → Ln-1 → L2 → Ln-2 → …`

You can't just change the values in the nodes — rearrange the nodes themselves. Your function returns nothing; the test runner reads the list starting from the original head.""",
  examples=[E([1, 2, 3, 4], out=[1, 4, 2, 3]), E([1, 2, 3, 4, 5], out=[1, 5, 2, 4, 3])],
  constraints=["1 <= number of nodes <= 5 * 10^4", "1 <= Node.val <= 1000"],
  starter=LIST_DEF + '''class Solution:
    def reorderList(self, head: Optional[ListNode]) -> None:
        """
        Do not return anything, modify head in-place instead.
        """
        pass
''',
  hints=["The new order alternates between the front half (going forward) and the back half (going backward).",
         "Break it into three classic moves: (1) find the middle with slow/fast pointers, (2) reverse the second half, (3) weave the two halves together.",
         "Find the middle (`slow`). Set `second = slow.next; slow.next = None`, reverse `second`. Then with `first = head`, alternate: save both `next`s, `first.next = second; second.next = saved_first_next`, advance both."],
  solution=LIST_DEF + r'''class Solution:
    def reorderList(self, head: Optional[ListNode]) -> None:
        slow, fast = head, head.next
        while fast and fast.next:
            slow, fast = slow.next, fast.next.next
        second, slow.next = slow.next, None
        prev = None
        while second:
            second.next, prev, second = prev, second, second.next
        first, second = head, prev
        while second:
            n1, n2 = first.next, second.next
            first.next, second.next = second, n1
            first, second = n1, n2
''',
  complexity="O(n) time, O(1) space",
  driver='''def drive(args):
    head = build_list(args[0])
    Solution().reorderList(head)
    return list_to_arr(head)
''',
  gen=_reorder_gen)


def _nth_gen(r):
    cases = [[[1, 2], 2], [[1, 2, 3], 3], [[1, 2, 3], 1]]
    for n in [4, 6, 10, 20, 30]:
        cases.append([rand_ints(r, n, 0, 100), r.randint(1, n)])
    return cases


P(id=23, slug="remove-nth-node-from-end-of-list", title="Remove Nth Node From End of List", lc=19, difficulty="Medium",
  category="Linked List", method="removeNthFromEnd", params=["head", "n"],
  description="""Given the `head` of a linked list, remove the `n`th node **from the end** of the list and return the head.

*Follow-up:* can you do it in one pass?""",
  examples=[E([1, 2, 3, 4, 5], 2, out=[1, 2, 3, 5]), E([1], 1, out=[]), E([1, 2], 1, out=[1])],
  constraints=["1 <= size of list <= 30", "0 <= Node.val <= 100", "1 <= n <= size of list"],
  starter=LIST_DEF + '''class Solution:
    def removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]:
        pass
''',
  hints=["Two passes works: count the length, then walk to the node just before the one to delete. Can you avoid counting?",
         "Use two pointers with a gap of `n` nodes between them. When the front pointer hits the end, the back pointer is right before the target. A dummy node handles deleting the head.",
         "`dummy = ListNode(0, head)`; `left = dummy`, `right = head`. Move `right` forward `n` times. Then move both until `right` is `None`. Now `left.next = left.next.next`. Return `dummy.next`."],
  solution=LIST_DEF + r'''class Solution:
    def removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]:
        dummy = ListNode(0, head)
        left, right = dummy, head
        for _ in range(n):
            right = right.next
        while right:
            left, right = left.next, right.next
        left.next = left.next.next
        return dummy.next
''',
  complexity="O(n) time, O(1) space",
  driver='''def drive(args):
    return list_to_arr(Solution().removeNthFromEnd(build_list(args[0]), args[1]))
''',
  gen=_nth_gen)


def _mergek_gen(r):
    cases = [[[[], [1]]], [[[2], [], [1]]], [[[1, 1], [1, 1], [1]]]]
    for k, n in [(2, 3), (3, 5), (5, 10), (10, 20), (100, 50)]:
        cases.append([[sorted(rand_ints(r, r.randint(0, n), -10**4, 10**4)) for _ in range(k)]])
    return cases


P(id=24, slug="merge-k-sorted-lists", title="Merge k Sorted Lists", lc=23, difficulty="Hard", category="Linked List",
  method="mergeKLists", params=["lists"],
  description="""You're given an array of `k` linked lists, each sorted in ascending order.

Merge all of them into one sorted linked list and return its head.""",
  examples=[E([[1, 4, 5], [1, 3, 4], [2, 6]], out=[1, 1, 2, 3, 4, 4, 5, 6]), E([], out=[]), E([[]], out=[])],
  constraints=["0 <= k <= 10^4", "0 <= lists[i].length <= 500", "-10^4 <= lists[i][j] <= 10^4", "Each list is sorted ascending; total nodes <= 10^4."],
  starter=LIST_DEF + '''class Solution:
    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
        pass
''',
  hints=["You already know how to merge *two* sorted lists. How could you build on that?",
         "Option A: merge lists in pairs, round after round (like merge sort) — O(N log k). Option B: keep the current head of every list in a min-heap.",
         "Heap approach: push `(node.val, i, node)` for each non-empty list (`i` breaks ties so nodes are never compared). Pop the smallest, attach it to your result, and push that node's `next` if it exists."],
  solution=LIST_DEF + r'''class Solution:
    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
        heap = [(node.val, i, node) for i, node in enumerate(lists) if node]
        heapq.heapify(heap)
        dummy = tail = ListNode()
        while heap:
            _, i, node = heapq.heappop(heap)
            tail.next = tail = node
            if node.next:
                heapq.heappush(heap, (node.next.val, i, node.next))
        return dummy.next
''',
  complexity="O(N log k) time, O(k) space",
  driver='''def drive(args):
    return list_to_arr(Solution().mergeKLists([build_list(a) for a in args[0]]))
''',
  gen=_mergek_gen)
