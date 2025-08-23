from utilities.choices import ChoiceSet


__all__ = (
    "DataFlowInheritedStatusChoices",
    "DataFlowProtocolChoices",
    "DataFlowStatusChoices",
    "ICMPv4TypeChoices",
    "ICMPv6TypeChoices",
    "TargetIsEmptyChoice",
)


class DataFlowProtocolChoices(ChoiceSet):
    """List of protocols allowed for data flows."""

    # Enable dynamic configuration
    key = "DataFlow.protocol"

    PROTOCOL_ANY = "any"
    PROTOCOL_ICMPv4 = "icmp"
    PROTOCOL_ICMPv6 = "icmpv6"
    PROTOCOL_TCP = "tcp"
    PROTOCOL_UDP = "udp"
    PROTOCOL_TCP_UDP = "tcp+udp"
    PROTOCOL_SCTP = "sctp"

    CHOICES = [
        (PROTOCOL_ANY, "Any"),
        (PROTOCOL_ICMPv4, "ICMPv4"),
        (PROTOCOL_ICMPv6, "ICMPv6"),
        (PROTOCOL_TCP, "TCP"),
        (PROTOCOL_UDP, "UDP"),
        (PROTOCOL_TCP_UDP, "TCP+UDP"),
        (PROTOCOL_SCTP, "SCTP"),
    ]


class ICMPv4TypeChoices(ChoiceSet):
    """List of ICMPv4 types allowed for data flows with protocol ICMPv4.

    Only common types are enabled by default. Use FIELD_CHOICES to expand if necessary.

    Reference: https://www.iana.org/assignments/icmp-parameters/icmp-parameters.xhtml
    """

    # Enable dynamic configuration
    key = "DataFlow.icmpv4types"

    TYPE_ECHO_REPLY = 0
    TYPE_DESTINATION_UNREACHABLE = 3
    TYPE_REDIRECT = 5
    TYPE_ECHO = 8
    TYPE_ROUTER_ADVERTISEMENT = 9
    TYPE_ROUTER_SOLICITATION = 10
    TYPE_TIME_EXCEEDED = 11
    TYPE_PARAMETER_PROBLEM = 12
    TYPE_TIMESTAMP = 13
    TYPE_TIMESTAMP_REPLY = 14

    CHOICES = [
        (TYPE_ECHO_REPLY, "Echo Reply (0)"),
        (TYPE_DESTINATION_UNREACHABLE, "Destination Unreachable (3)"),
        (TYPE_REDIRECT, "Redirect Message (5)"),
        (TYPE_ECHO, "Echo Request (8)"),
        (TYPE_ROUTER_ADVERTISEMENT, "Router Advertisement (9)"),
        (TYPE_ROUTER_SOLICITATION, "Router Solicitation (10)"),
        (TYPE_TIME_EXCEEDED, "Time Exceeded (11)"),
        (TYPE_PARAMETER_PROBLEM, "Parameter Problem (12)"),
        (TYPE_TIMESTAMP, "Timestamp (13)"),
        (TYPE_TIMESTAMP_REPLY, "Timestamp Reply (14)"),
    ]


class ICMPv6TypeChoices(ChoiceSet):
    """List of ICMPv6 types allowed for data flows with protocol ICMPv4.

    Only common types are enabled by default. Use FIELD_CHOICES to expand if necessary.

    Reference: https://www.iana.org/assignments/icmpv6-parameters/icmpv6-parameters.xhtml
    """

    # Enable dynamic configuration
    key = "DataFlow.icmpv6types"

    # errors
    TYPE_DESTINATION_UNREACHABLE = 1
    TYPE_PACKET_TOO_BIG = 2
    TYPE_TIME_EXCEEDED = 3
    TYPE_PARAMETER_PROBLEM = 4

    # informations
    TYPE_ECHO = 128
    TYPE_ECHO_REPLY = 129
    TYPE_MULTICAST_LISTENER_QUERY = 130
    TYPE_MULTICAST_LISTENER_REPORT = 131
    TYPE_MULTICAST_LISTENER_DONE = 132
    TYPE_ROUTER_SOLICITATION = 133
    TYPE_ROUTER_ADVERTISEMENT = 134
    TYPE_NEIGHBOR_SOLICITATION = 135
    TYPE_NEIGHBOR_ADVERTISEMENT = 136
    TYPE_REDIRECT = 137
    TYPE_MULTICAST_LISTENER_REPORT_V2 = 143

    CHOICES = [
        (TYPE_DESTINATION_UNREACHABLE, "Destination Unreachable (1)"),
        (TYPE_PACKET_TOO_BIG, "Packet Too Big (2)"),
        (TYPE_TIME_EXCEEDED, "Time Exceeded (3)"),
        (TYPE_PARAMETER_PROBLEM, "Parameter Problem (4)"),
        (TYPE_ECHO, "Echo Request (128)"),
        (TYPE_ECHO_REPLY, "Echo Reply (129)"),
        (TYPE_MULTICAST_LISTENER_QUERY, "Multicast Listener Query (130)"),
        (TYPE_MULTICAST_LISTENER_REPORT, "Multicast Listener Report (131)"),
        (TYPE_MULTICAST_LISTENER_DONE, "Multicast Listener Done (132)"),
        (TYPE_ROUTER_SOLICITATION, "Router Solicitation (133)"),
        (TYPE_ROUTER_ADVERTISEMENT, "Router Advertisement (134)"),
        (TYPE_NEIGHBOR_SOLICITATION, "Neighbor Solicitation (135)"),
        (TYPE_NEIGHBOR_ADVERTISEMENT, "Neighbor Advertisement (136)"),
        (TYPE_REDIRECT, "Redirect Message (137)"),
        (TYPE_MULTICAST_LISTENER_REPORT_V2, "Multicast Listener Report v2 (143)"),
    ]


class DataFlowStatusChoices(ChoiceSet):
    """List of statuses for data flows and groups."""

    STATUS_ENABLED = "enabled"
    STATUS_DISABLED = "disabled"

    CHOICES = (
        (STATUS_ENABLED, "Enabled", "green"),
        (STATUS_DISABLED, "Disabled", "red"),
    )


class DataFlowInheritedStatusChoices(DataFlowStatusChoices):
    """List of inherited statuses for data flows and groups."""

    STATUS_ENABLED = "enabled"
    STATUS_DISABLED = "disabled"
    STATUS_INHERITED_DISABLED = "disabled-parent"

    CHOICES = (
        (STATUS_ENABLED, "Enabled", "green"),
        (STATUS_DISABLED, "Disabled", "red"),
        (STATUS_INHERITED_DISABLED, "Disabled (Inherited)", "orange"),
    )


class TargetIsEmptyChoice(ChoiceSet):
    """List of statuses for null target, for forms."""

    STATUS_NULL = "true"
    STATUS_NOT_NULL = "false"

    CHOICES = (
        (STATUS_NULL, "Null"),
        (STATUS_NOT_NULL, "Not null"),
    )
