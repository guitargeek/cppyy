import py, os, sys
from pytest import raises
from .support import setup_make

currpath = py.path.local(__file__).dirpath()
test_dct = str(currpath.join("templatesDict.so"))

def setup_module(mod):
    setup_make("templatesDict.so")


class TestTEMPLATES:
    def setup_class(cls):
        cls.test_dct = test_dct
        import cppyy
        cls.templates = cppyy.load_reflection_info(cls.test_dct)

    def test01_template_member_functions(self):
        """Template member functions lookup and calls"""

        import cppyy

        m = cppyy.gbl.MyTemplatedMethodClass()

      # pre-instantiated
        assert m.get_size['char']()   == m.get_char_size()
        assert m.get_size[int]()      == m.get_int_size()

      # specialized
        if sys.hexversion >= 0x3000000:
            targ = 'long'
        else:
            targ = long
        assert m.get_size[targ]()     == m.get_long_size()

      # auto-instantiation
        assert m.get_size[float]()    == m.get_float_size()
        assert m.get_size['double']() == m.get_double_size()
        assert m.get_size['MyTemplatedMethodClass']() == m.get_self_size()

      # auto through typedef
        assert m.get_size['MyTMCTypedef_t']() == m.get_self_size()

    def test02_non_type_template_args(self):
        """Use of non-types as template arguments"""

        import cppyy

        cppyy.cppdef("template<int i> int nt_templ_args() { return i; };")

        assert cppyy.gbl.nt_templ_args[1]()   == 1
        assert cppyy.gbl.nt_templ_args[256]() == 256

    def test03_templated_function(self):
        """Templated global and static functions lookup and calls"""

        import cppyy

        # TODO: the following only works if something else has already
        # loaded the headers associated with this template
        ggs = cppyy.gbl.global_get_size
        assert ggs['char']() == 1

        gsf = cppyy.gbl.global_some_foo

        assert gsf[int](3) == 42
        assert gsf(3)      == 42
        assert gsf(3.)     == 42

        gsb = cppyy.gbl.global_some_bar

        assert gsb(3)            == 13
        assert gsb['double'](3.) == 13

        # TODO: the following only works in a namespace
        nsgsb = cppyy.gbl.SomeNS.some_bar

        assert nsgsb[3]
        assert nsgsb[3]() == 3

        # TODO: add some static template method

    def test04_variadic_function(self):
        """Call a variadic function"""

        import cppyy

        s = cppyy.gbl.std.ostringstream()
        #s << '('
        #cppyy.gbl.SomeNS.tuplify(s, 1, 4., "aap")
        #print(s.str())

    def test05_variadic_overload(self):
        """Call an overloaded variadic function"""

        import cppyy

        assert cppyy.gbl.isSomeInt(3.)         == False
        assert cppyy.gbl.isSomeInt(1)          == True
        assert cppyy.gbl.isSomeInt()           == False
        assert cppyy.gbl.isSomeInt(1, 2, 3)    == False

    def test06_variadic_sfinae(self):
        """Attribute testing through SFINAE"""

        import cppyy
        cppyy.gbl.AttrTesting      # load
        from cppyy.gbl.AttrTesting import Obj1, Obj2, has_var1, call_has_var1
        from cppyy.gbl.std import move

        assert has_var1(Obj1()) == hasattr(Obj1(), 'var1')
        assert has_var1(Obj2()) == hasattr(Obj2(), 'var1')
        assert has_var1(3)      == hasattr(3,      'var1')
        assert has_var1("aap")  == hasattr("aap",  'var1')

        assert call_has_var1(move(Obj1())) == True
        assert call_has_var1(move(Obj2())) == False
        
