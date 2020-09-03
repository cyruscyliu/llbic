"""
Copyright (c) 2015, The Regents of the University of California
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
"""


class Component(object):
    """
        Base component that need to be used by all components to be used.
    """

    def setup(self):
        """
            Perform setup.
        :return: msg if the Setup Failed else None.
        """
        return None

    def perform(self):
        """
            Perform the tasks needed for the component.
        :return:
        """
        raise NotImplementedError("Perform needs to be implemented.")

    def cleanup(self):
        """
            Perform clean up.
        :return: msg if the cleanup Failed else None.
        """
        return None

    def get_name(self):
        """
            Get the name of the component
        :return: String representing component name.
        """
        return "NoName"

    def is_critical(self):
        """
            Is the component critical?
            If true, then failure of this component is treated as fatal.
        :return: True if the component is critical else false.
        """
        return False
