import unittest
from unittest.mock import patch, call
from protestr import provide


class Tearable:
    def __init__(self):
        self.torndown = False

    def __teardown__(self):
        self.torndown = True


class TestProvider(unittest.TestCase):
    @patch("protestr.resolve")
    def test_provide(self, resolve):
        resolved_tearables = [
            Tearable(), Tearable(), Tearable()
        ]

        resolved_tearable_lists = [
            [Tearable(), Tearable()],
            [Tearable(), Tearable()],
            [Tearable(), Tearable(), Tearable()],
        ]

        resolved_values = ["string1", "string2", 1]

        resolved_value_lists = [
            ["string3", "string4"],
            ["string5", "string6"],
            ["string7", "string8", "string9"]
        ]

        resolved_overridden_tearable_lists = [
            [Tearable()], [Tearable()], [Tearable()]
        ]

        resolved_additional_tearable_lists = [
            [Tearable()], [Tearable()], [Tearable()]
        ]

        resolve.side_effect = [
            "literal",
            resolved_tearables[0],
            resolved_tearable_lists[0],
            resolved_values[0],
            resolved_value_lists[0],
            resolved_overridden_tearable_lists[0],
            resolved_additional_tearable_lists[0],

            "literal",
            resolved_tearables[1],
            resolved_tearable_lists[1],
            resolved_values[1],
            resolved_value_lists[1],
            resolved_overridden_tearable_lists[1],
            resolved_additional_tearable_lists[1],

            "another literal",
            resolved_tearables[2],
            resolved_tearable_lists[2],
            resolved_values[2],
            resolved_value_lists[2],
            resolved_overridden_tearable_lists[2],
            resolved_additional_tearable_lists[2]
        ]

        ignored = Tearable()

        provided = provide(
            literal="another literal",
            tearable=Tearable,
            tearables=3*[Tearable],
            spec=int,
            specs=3*[str],
            to_override=ignored,
        )(
            provide(
                to_override=ignored
            )(
                provide(
                    literal="literal",
                    tearable=Tearable,
                    tearables=2*[Tearable],
                    spec=str,
                    specs=2*[str],
                    to_override=ignored,
                )(
                    lambda *args, **kwds: (args, kwds)
                )
            )
        )

        def untouched(): pass

        (arg,), kwds = provided(
            untouched,
            to_override=[Tearable],
            additional_kwd=[Tearable]
        )

        self.assertEqual(
            resolve.mock_calls, [
                call("literal"),
                call(Tearable),
                call(2*[Tearable]),
                call(str),
                call(2*[str]),
                call([Tearable]),
                call([Tearable]),

                call("literal"),
                call(Tearable),
                call(2*[Tearable]),
                call(str),
                call(2*[str]),
                call([Tearable]),
                call([Tearable]),

                call("another literal"),
                call(Tearable),
                call(3*[Tearable]),
                call(int),
                call(3*[str]),
                call([Tearable]),
                call([Tearable])
            ]
        )

        self.assertEqual(arg, untouched)

        self.assertEqual(
            [*kwds], [
                "literal",
                "tearable",
                "tearables",
                "spec",
                "specs",
                "to_override",
                "additional_kwd"
            ]
        )

        self.assertEqual(kwds["literal"], "another literal")

        self.assertEqual(kwds["tearable"], resolved_tearables[2])

        self.assertEqual(
            kwds["tearables"],
            resolved_tearable_lists[2]
        )

        self.assertEqual(kwds["spec"], resolved_values[2])

        self.assertEqual(kwds["specs"], resolved_value_lists[2])

        self.assertEqual(
            kwds["to_override"],
            resolved_overridden_tearable_lists[2]
        )

        self.assertEqual(
            kwds["additional_kwd"],
            resolved_additional_tearable_lists[2]
        )

        self.assertTrue(all(x.torndown for x in resolved_tearables))

        self.assertTrue(
            all(
                x.torndown
                for li in resolved_tearable_lists
                for x in li
            )
        )

        self.assertTrue(
            all(
                x.torndown
                for li in resolved_overridden_tearable_lists
                for x in li
            )
        )

        self.assertTrue(
            all(
                x.torndown
                for li in resolved_additional_tearable_lists
                for x in li
            )
        )

        self.assertFalse(ignored.torndown)


if __name__ == "__main__":
    unittest.main()
