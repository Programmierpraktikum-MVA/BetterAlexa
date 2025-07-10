#include <pybind11/pybind11.h>
#include "meeting_sdk.h" // or the relevant header

namespace py = pybind11;

PYBIND11_MODULE(meeting_sdk, m) {
    m.def("get_user_id", &getUserID, "Get the user ID from the meeting SDK");
}
